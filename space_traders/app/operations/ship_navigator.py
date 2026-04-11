from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from app.core.fleet_manager import ShipRole, TrackedShip


class ShipActivity(Enum):
    IDLE = "idle"
    TRAVELING = "traveling"
    MINING = "mining"
    TRADING = "trading"
    REFINING = "refining"
    SURVEYING = "surveying"
    EXPLORING = "exploring"
    DOCKED = "docked"


@dataclass
class ShipNavigationState:
    ship_symbol: str
    activity: ShipActivity = ShipActivity.IDLE
    destination: Optional[str] = None
    departure_time: Optional[datetime] = None
    estimated_arrival: Optional[datetime] = None
    navigation_errors: int = 0
    last_waypoint: Optional[str] = None

    def navigate_to(self, waypoint: str, estimated_seconds: int = 60) -> None:
        self.activity = ShipActivity.TRAVELING
        self.destination = waypoint
        self.departure_time = datetime.now()
        self.estimated_arrival = datetime.now().replace(microsecond=0) + timedelta(seconds=estimated_seconds)

    def arrive(self) -> None:
        self.destination = None
        self.departure_time = None
        self.estimated_arrival = None

    def set_activity(self, activity: ShipActivity) -> None:
        self.activity = activity
        if activity != ShipActivity.TRAVELING:
            self.destination = None

    def is_traveling(self) -> bool:
        return self.activity == ShipActivity.TRAVELING

    def should_have_arrived(self) -> bool:
        if not self.estimated_arrival:
            return False
        return datetime.now() > self.estimated_arrival


class ShipNavigator:
    _instance: Optional["ShipNavigator"] = None

    def __init__(self):
        self._ship_states: dict[str, ShipNavigationState] = {}

    @classmethod
    def get_instance(cls) -> "ShipNavigator":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_state(self, ship_symbol: str) -> ShipNavigationState:
        if ship_symbol not in self._ship_states:
            self._ship_states[ship_symbol] = ShipNavigationState(ship_symbol=ship_symbol)
        return self._ship_states[ship_symbol]

    def navigate_ship(
        self,
        ship: TrackedShip,
        destination: str,
        estimated_seconds: int = 60,
    ) -> dict:
        state = self.get_state(ship.symbol)
        state.navigate_to(destination, estimated_seconds)
        ship.is_busy = True
        ship.last_action = f"traveling to {destination}"

        return {
            "success": True,
            "ship": ship.symbol,
            "destination": destination,
            "estimated_arrival": state.estimated_arrival.isoformat() if state.estimated_arrival else None,
        }

    def ship_arrived(self, ship_symbol: str) -> None:
        state = self._ship_states.get(ship_symbol)
        if state:
            state.arrive()
        self._ship_states[ship_symbol] = ShipNavigationState(ship_symbol=ship_symbol)
        self._ship_states[ship_symbol].last_waypoint = state.destination if state else None

    def set_activity(
        self,
        ship_symbol: str,
        activity: ShipActivity,
        ship: TrackedShip | None = None,
    ) -> None:
        state = self.get_state(ship_symbol)
        state.set_activity(activity)
        if ship:
            ship.is_busy = activity != ShipActivity.IDLE

    def mark_error(self, ship_symbol: str) -> None:
        state = self.get_state(ship_symbol)
        state.navigation_errors += 1

    def is_traveling(self, ship_symbol: str) -> bool:
        state = self._ship_states.get(ship_symbol)
        return state.is_traveling() if state else False

    def get_traveling_ships(self) -> list[str]:
        return [s for s, state in self._ship_states.items() if state.is_traveling()]

    def get_idle_ships(self, role: ShipRole | None = None) -> list[str]:
        idle = []
        for ship_symbol, state in self._ship_states.items():
            if state.activity == ShipActivity.IDLE:
                idle.append(ship_symbol)
        return idle

    def cancel_navigation(self, ship_symbol: str) -> None:
        if ship_symbol in self._ship_states:
            del self._ship_states[ship_symbol]

    def get_stats(self) -> dict:
        traveling = sum(1 for s in self._ship_states.values() if s.is_traveling())
        idle = sum(1 for s in self._ship_states.values() if s.activity == ShipActivity.IDLE)
        mining = sum(1 for s in self._ship_states.values() if s.activity == ShipActivity.MINING)
        trading = sum(1 for s in self._ship_states.values() if s.activity == ShipActivity.TRADING)

        return {
            "total_tracked": len(self._ship_states),
            "traveling": traveling,
            "idle": idle,
            "mining": mining,
            "trading": trading,
        }
