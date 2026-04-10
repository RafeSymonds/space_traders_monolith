from dataclasses import dataclass
from enum import Enum
from typing import Optional

from space_traders_api import FleetApi
from space_traders_api.models import Ship


class ShipRole(Enum):
    MINING = "mining"
    GAS_SIPHONING = "gas_siphoning"
    TRADING = "trading"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    TRANSPORT = "transport"
    REFINING = "refining"
    COMMAND = "command"
    CARRIER = "carrier"


@dataclass
class TrackedShip:
    ship: Ship
    role: ShipRole = ShipRole.TRANSPORT
    current_waypoint: str | None = None
    system: str | None = None
    is_busy: bool = False
    last_action: str | None = None

    @property
    def symbol(self) -> str:
        return self.ship.symbol

    @property
    def cargo_capacity(self) -> int:
        return self.ship.cargo.capacity if self.ship.cargo else 0

    @property
    def cargo_used(self) -> int:
        return self.ship.cargo.units if self.ship.cargo else 0

    @property
    def cargo_available(self) -> int:
        return self.cargo_capacity - self.cargo_used


class FleetManager:
    _instance: Optional["FleetManager"] = None

    def __init__(self):
        self.ships: dict[str, TrackedShip] = {}
        self._fleet_api: FleetApi | None = None

    @classmethod
    def get_instance(cls) -> "FleetManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_fleet_api(self, api: FleetApi):
        self._fleet_api = api

    def add_ship(self, ship: Ship, role: ShipRole = ShipRole.TRANSPORT) -> TrackedShip:
        tracked = TrackedShip(
            ship=ship,
            role=role,
            current_waypoint=ship.nav.waypoint_symbol if ship.nav else None,
            system=ship.nav.system_symbol if ship.nav else None,
        )
        self.ships[ship.symbol] = tracked
        return tracked

    def get_ship(self, symbol: str) -> TrackedShip | None:
        return self.ships.get(symbol)

    def get_ships_by_role(self, role: ShipRole) -> list[TrackedShip]:
        return [s for s in self.ships.values() if s.role == role]

    def get_available_ships(self, role: ShipRole | None = None) -> list[TrackedShip]:
        ships = [s for s in self.ships.values() if not s.is_busy]
        if role:
            ships = [s for s in ships if s.role == role]
        return ships

    def refresh_ship(self, ship: Ship):
        if ship.symbol in self.ships:
            tracked = self.ships[ship.symbol]
            tracked.ship = ship
            tracked.current_waypoint = ship.nav.waypoint_symbol if ship.nav else None
            tracked.system = ship.nav.system_symbol if ship.nav else None

    async def refresh_all_ships(self):
        if not self._fleet_api:
            return
        result = self._fleet_api.get_my_ships()
        for ship_data in result.data:
            if ship_data.symbol in self.ships:
                self.refresh_ship(ship_data)


fleet_manager = FleetManager.get_instance()
