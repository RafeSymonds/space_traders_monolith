from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from space_traders_api import SystemsApi
from space_traders_api.models import WaypointType


class WaypointTypeEnum(Enum):
    ASTEROID_FIELD = "ASTEROID_FIELD"
    CIRCULAR_ORBIT = "CIRCULAR_ORBIT"
    NEBULA = "NEBULA"
    PLANET = "PLANET"
    GAS_GIANT = "GAS_GIANT"
    MOON = "MOON"
    RING = "RING"
    SPACE_STATION = "SPACE_STATION"
    CONSTRUCTED_WAYPOINT = "CONSTRUCTED_WAYPOINT"
    GRAVITY_RIFT = "GRAVITY_RIFT"
    SHIPYARD = "SHIPYARD"
    MARKETPLACE = "MARKETPLACE"
    JUMP_GATE = "JUMP_GATE"
    ENGINEERED_ASTEROID = "ENGINEERED_ASTEROID"
    Asteroid = "ASTEROID_FIELD"
    Orbit = "ORBIT"
    JumpGate = "JUMP_GATE"


@dataclass
class WaypointTrait:
    symbol: str
    name: str
    description: str


@dataclass
class WaypointInfo:
    symbol: str
    type: str
    system_symbol: str
    x: int
    y: int
    traits: list[WaypointTrait]
    orbitals: list[str] = field(default_factory=list)
    faction: Optional[str] = None
    has_been_visited: bool = False
    market_data_fetched_at: Optional[datetime] = None

    @property
    def is_marketplace(self) -> bool:
        return any(t.symbol == "MARKETPLACE" for t in self.traits)

    @property
    def is_asteroid_field(self) -> bool:
        if self.type in ("ASTEROID_FIELD", "ASTEROID", "ASTEROID_BASE"):
            return True
        return any(t.symbol == "ASTEROID_FIELD" for t in self.traits)

    @property
    def is_shipyard(self) -> bool:
        return any(t.symbol == "SHIPYARD" for t in self.traits)

    @property
    def is_jump_gate(self) -> bool:
        return any(t.symbol == "JUMP_GATE" for t in self.traits)

    @property
    def market_data_stale(self) -> bool:
        if not self.market_data_fetched_at:
            return True
        age = datetime.now() - self.market_data_fetched_at
        return age.total_seconds() > 300


class WaypointRegistry:
    _instance: Optional["WaypointRegistry"] = None

    def __init__(self):
        self._waypoints: dict[str, WaypointInfo] = {}
        self._systems_scanned: set[str] = set()
        self._last_scan: dict[str, datetime] = {}

    @classmethod
    def get_instance(cls) -> "WaypointRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def add_waypoint(self, waypoint_data, system_symbol: str) -> WaypointInfo:
        traits = []
        if hasattr(waypoint_data, "traits") and waypoint_data.traits:
            for t in waypoint_data.traits:
                trait = WaypointTrait(
                    symbol=t.symbol.value if hasattr(t.symbol, "value") else str(t.symbol),
                    name=getattr(t, "name", ""),
                    description=getattr(t, "description", ""),
                )
                traits.append(trait)

        waypoint_type = ""
        if hasattr(waypoint_data, "type"):
            if hasattr(waypoint_data.type, "value"):
                waypoint_type = waypoint_data.type.value
            else:
                waypoint_type = str(waypoint_data.type)

        waypoint = WaypointInfo(
            symbol=waypoint_data.symbol,
            type=waypoint_type,
            system_symbol=system_symbol,
            x=getattr(waypoint_data, "x", 0),
            y=getattr(waypoint_data, "y", 0),
            traits=traits,
            orbitals=getattr(waypoint_data, "orbitals", []) or [],
            faction=getattr(waypoint_data, "faction", None),
        )

        if waypoint.symbol in self._waypoints:
            existing = self._waypoints[waypoint.symbol]
            waypoint.has_been_visited = existing.has_been_visited
            waypoint.market_data_fetched_at = existing.market_data_fetched_at

        self._waypoints[waypoint.symbol] = waypoint
        return waypoint

    def get_waypoint(self, symbol: str) -> WaypointInfo | None:
        return self._waypoints.get(symbol)

    def get_waypoints_in_system(self, system_symbol: str) -> list[WaypointInfo]:
        return [w for w in self._waypoints.values() if w.system_symbol == system_symbol]

    def get_marketplaces(self, system_symbol: str | None = None) -> list[WaypointInfo]:
        waypoints = self._waypoints.values()
        if system_symbol:
            waypoints = [w for w in waypoints if w.system_symbol == system_symbol]
        return [w for w in waypoints if w.is_marketplace]

    def get_asteroid_fields(self, system_symbol: str | None = None) -> list[WaypointInfo]:
        waypoints = self._waypoints.values()
        if system_symbol:
            waypoints = [w for w in waypoints if w.system_symbol == system_symbol]
        return [w for w in waypoints if w.is_asteroid_field]

    def get_shipyards(self, system_symbol: str | None = None) -> list[WaypointInfo]:
        waypoints = self._waypoints.values()
        if system_symbol:
            waypoints = [w for w in waypoints if w.system_symbol == system_symbol]
        return [w for w in waypoints if w.is_shipyard]

    def get_jump_gates(self, system_symbol: str | None = None) -> list[WaypointInfo]:
        waypoints = self._waypoints.values()
        if system_symbol:
            waypoints = [w for w in waypoints if w.system_symbol == system_symbol]
        return [w for w in waypoints if w.is_jump_gate]

    def get_unvisited_marketplaces(self, system_symbol: str | None = None) -> list[WaypointInfo]:
        marketplaces = self.get_marketplaces(system_symbol)
        return [m for m in marketplaces if not m.has_been_visited]

    def mark_visited(self, waypoint_symbol: str) -> None:
        if waypoint_symbol in self._waypoints:
            self._waypoints[waypoint_symbol].has_been_visited = True

    def mark_market_scanned(self, waypoint_symbol: str) -> None:
        if waypoint_symbol in self._waypoints:
            self._waypoints[waypoint_symbol].market_data_fetched_at = datetime.now()

    def system_needs_scan(self, system_symbol: str) -> bool:
        if system_symbol not in self._systems_scanned:
            return True
        last = self._last_scan.get(system_symbol)
        if not last:
            return True
        return (datetime.now() - last).total_seconds() > 3600

    def mark_system_scanned(self, system_symbol: str) -> None:
        self._systems_scanned.add(system_symbol)
        self._last_scan[system_symbol] = datetime.now()

    def scan_system(self, systems_api: SystemsApi, system_symbol: str) -> list[WaypointInfo]:
        try:
            result = systems_api.get_system_waypoints(system_symbol=system_symbol)
            waypoints = []
            for wp in result.data or []:
                waypoint = self.add_waypoint(wp, system_symbol)
                waypoints.append(waypoint)
            self.mark_system_scanned(system_symbol)
            return waypoints
        except Exception:
            return []

    def distance(self, waypoint1: str, waypoint2: str) -> float:
        w1 = self.get_waypoint(waypoint1)
        w2 = self.get_waypoint(waypoint2)
        if not w1 or not w2:
            return float("inf")
        return ((w1.x - w2.x) ** 2 + (w1.y - w2.y) ** 2) ** 0.5

    def get_closest_waypoint(self, from_symbol: str, waypoint_type: str | None = None) -> WaypointInfo | None:
        from_wp = self.get_waypoint(from_symbol)
        if not from_wp:
            return None

        candidates = self._waypoints.values()
        if waypoint_type:
            candidates = [w for w in candidates if w.type == waypoint_type]

        if not candidates:
            return None

        return min(candidates, key=lambda w: ((w.x - from_wp.x) ** 2 + (w.y - from_wp.y) ** 2) ** 0.5)

    def get_all(self) -> list[WaypointInfo]:
        return list(self._waypoints.values())

    def get_stats(self) -> dict:
        total = len(self._waypoints)
        visited = sum(1 for w in self._waypoints.values() if w.has_been_visited)
        with_market = sum(1 for w in self._waypoints.values() if w.market_data_fetched_at)
        return {
            "total_waypoints": total,
            "visited": visited,
            "market_data_fetched": with_market,
            "systems_scanned": len(self._systems_scanned),
        }
