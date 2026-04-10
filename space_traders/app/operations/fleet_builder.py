from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from space_traders_api import FleetApi


class ShipPurchaseState(Enum):
    IDLE = "idle"
    FINDING_DEAL = "finding_deal"
    PURCHASING = "purchasing"
    DEPLOYING = "deploying"
    ERROR = "error"


@dataclass
class ShipPurchaseResult:
    success: bool
    ship_symbol: str | None = None
    price: int = 0
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class ShipPurchaser:
    def __init__(
        self,
        fleet_api: FleetApi,
        min_credits_before_buy: int = 50000,
        preferred_ships: list[str] | None = None,
    ):
        self._fleet = fleet_api
        self._min_credits = min_credits_before_buy
        self._preferred_ships = preferred_ships or [
            "SHIP_MINING_DRONE",
            "SHIP_HOOVER",
            "SHIP_LIGHT_FREIGHTER",
            "SHIP_PROBE",
            "SHIP_RECON",
        ]
        self._state = ShipPurchaseState.IDLE
        self._last_error: str | None = None

    def get_state(self) -> ShipPurchaseState:
        return self._state

    def can_purchase(self, current_credits: int) -> bool:
        return current_credits >= self._min_credits

    def get_available_ships(self, agent: dict) -> list[dict]:
        try:
            result = self._fleet.get_ship_types()
            ships = []
            for ship_type in result.data or []:
                if ship_type.price <= agent.get("credits", 0) * 0.3:
                    ships.append(
                        {
                            "symbol": ship_type.type,
                            "name": ship_type.name,
                            "price": ship_type.price,
                            "description": getattr(ship_type, "description", "")[:100],
                        },
                    )
            return sorted(ships, key=lambda x: x["price"])
        except Exception:
            return []

    def purchase_ship(
        self,
        ship_type: str,
        waypoint: str,
    ) -> ShipPurchaseResult:
        self._state = ShipPurchaseState.PURCHASING
        try:
            result = self._fleet.purchase_ship(
                purchase_request={
                    "ship_type": ship_type,
                    "waypoint_symbol": waypoint,
                },
            )

            if result.data and result.data.agent:
                ship = result.data.ship
                self._state = ShipPurchaseState.IDLE
                return ShipPurchaseResult(
                    success=True,
                    ship_symbol=ship.symbol if ship else None,
                    price=getattr(ship, "purchase_price", 0),
                )

            self._state = ShipPurchaseState.ERROR
            return ShipPurchaseResult(success=False, error="Purchase failed")

        except Exception as e:
            self._state = ShipPurchaseState.ERROR
            self._last_error = str(e)
            return ShipPurchaseResult(success=False, error=str(e))

    def auto_purchase_if_able(
        self,
        agent: dict,
        purchase_waypoint: str,
    ) -> ShipPurchaseResult | None:
        credits = agent.get("credits", 0)

        if not self.can_purchase(credits):
            return None

        available = self.get_available_ships(agent)
        if not available:
            return None

        ship_type = available[0]["symbol"]
        self._state = ShipPurchaseState.FINDING_DEAL

        return self.purchase_ship(ship_type, purchase_waypoint)

    def get_stats(self) -> dict:
        return {
            "state": self._state.value,
            "min_credits_before_buy": self._min_credits,
            "preferred_ships": self._preferred_ships,
            "last_error": self._last_error,
        }


class FleetExpansionManager:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api
        self._purchaser = ShipPurchaser(fleet_api)
        self._total_ships_purchased = 0
        self._total_spent = 0
        self._purchase_history: list[ShipPurchaseResult] = []

    def get_total_ships(self) -> int:
        try:
            result = self._fleet.get_my_ships()
            return len(result.data) if result.data else 0
        except Exception:
            return 0

    def attempt_expansion(
        self,
        agent: dict,
        purchase_waypoint: str,
        target_fleet_size: int = 10,
    ) -> ShipPurchaseResult | None:
        current_count = self.get_total_ships()

        if current_count >= target_fleet_size:
            return None

        result = self._purchaser.auto_purchase_if_able(agent, purchase_waypoint)

        if result and result.success:
            self._total_ships_purchased += 1
            self._total_spent += result.price
            self._purchase_history.append(result)

        return result

    def get_expansion_stats(self) -> dict:
        return {
            "total_ships_purchased": self._total_ships_purchased,
            "total_credits_spent": self._total_spent,
            "current_purchaser_state": self._purchaser.get_state().value,
            "purchase_history": [
                {
                    "ship": r.ship_symbol,
                    "price": r.price,
                    "timestamp": r.timestamp.isoformat(),
                }
                for r in self._purchase_history[-10:]
            ],
        }
