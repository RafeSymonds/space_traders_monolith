from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from space_traders_api import FleetApi, SystemsApi


class ShipType(Enum):
    PROBE = "SHIP_PROBE"
    MINING_DRONE = "SHIP_MINING_DRONE"
    SIPHON_DRONE = "SHIP_SIPHON_DRONE"
    INTERCEPTOR = "SHIP_INTERCEPTOR"
    LIGHT_HAULER = "SHIP_LIGHT_HAULER"
    COMMAND_FRIGATE = "SHIP_COMMAND_FRIGATE"
    EXPLORER = "SHIP_EXPLORER"
    HEAVY_FREIGHTER = "SHIP_HEAVY_FREIGHTER"
    LIGHT_SHUTTLE = "SHIP_LIGHT_SHUTTLE"
    ORE_HOUND = "SHIP_ORE_HOUND"
    REFINING_FREIGHTER = "SHIP_REFINING_FREIGHTER"
    SURVEYOR = "SHIP_SURVEYOR"
    BULK_FREIGHTER = "SHIP_BULK_FREIGHTER"


SHIP_ROLE_MAP = {
    "PROBE": "exploration",
    "MINING_DRONE": "mining",
    "SIPHON_DRONE": "mining",
    "INTERCEPTOR": "combat",
    "LIGHT_HAULER": "transport",
    "COMMAND_FRIGATE": "command",
    "EXPLORER": "exploration",
    "HEAVY_FREIGHTER": "transport",
    "LIGHT_SHUTTLE": "transport",
    "ORE_HOUND": "mining",
    "REFINING_FREIGHTER": "refining",
    "SURVEYOR": "mining",
    "BULK_FREIGHTER": "transport",
}


@dataclass
class ShipListing:
    symbol: str
    name: str
    price: int
    description: str
    frame: str
    speed: int
    crew: dict
    cargo_capacity: int
    fuel_capacity: int


@dataclass
class ShipModule:
    symbol: str
    name: str
    description: str
    price: int
    module_type: str
    requirements: dict


@dataclass
class ShipMount:
    symbol: str
    name: str
    description: str
    price: int
    mount_type: str


@dataclass
class PurchaseResult:
    success: bool
    ship_symbol: str | None = None
    price: int = 0
    credits_remaining: int = 0
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class ShipyardService:
    def __init__(self, fleet_api: FleetApi, systems_api: SystemsApi):
        self._fleet = fleet_api
        self._systems = systems_api
        self._available_ships: dict[str, list[ShipListing]] = {}
        self._ship_prices: dict[str, int] = {}
        self._purchase_history: list[PurchaseResult] = []

    def get_shipyard_ships(
        self,
        system_symbol: str,
        waypoint_symbol: str,
    ) -> list[ShipListing]:
        cache_key = f"{system_symbol}:{waypoint_symbol}"
        if cache_key in self._available_ships:
            return self._available_ships[cache_key]

        try:
            result = self._systems.get_shipyard(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )

            ships = []
            if result.data and hasattr(result.data, "ships"):
                for ship in result.data.ships:
                    listing = ShipListing(
                        symbol=getattr(ship, "symbol", "UNKNOWN"),
                        name=getattr(ship, "name", "Unknown Ship"),
                        price=getattr(ship, "price", 0) or 0,
                        description=getattr(ship, "description", "")[:200],
                        frame=getattr(ship, "frame", "UNKNOWN"),
                        speed=getattr(ship, "speed", 0) or 0,
                        crew=getattr(ship, "crew", {}),
                        cargo_capacity=getattr(ship, "cargo_capacity", 0) or 0,
                        fuel_capacity=getattr(ship, "fuel_capacity", 0) or 0,
                    )
                    ships.append(listing)
                    self._ship_prices[listing.symbol] = listing.price

            self._available_ships[cache_key] = ships
            return ships

        except Exception:
            return []

    def get_shipyard_modules(
        self,
        system_symbol: str,
        waypoint_symbol: str,
    ) -> list[ShipModule]:
        try:
            result = self._systems.get_shipyard(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )

            modules = []
            if result.data and hasattr(result.data, "modules"):
                for mod in result.data.modules:
                    modules.append(
                        ShipModule(
                            symbol=getattr(mod, "symbol", "UNKNOWN"),
                            name=getattr(mod, "name", "Unknown Module"),
                            description=getattr(mod, "description", ""),
                            price=getattr(mod, "price", 0) or 0,
                            module_type=getattr(mod, "type", "UNKNOWN"),
                            requirements=getattr(mod, "requirements", {}),
                        ),
                    )

            return modules

        except Exception:
            return []

    def get_shipyard_mounts(
        self,
        system_symbol: str,
        waypoint_symbol: str,
    ) -> list[ShipMount]:
        try:
            result = self._systems.get_shipyard(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )

            mounts = []
            if result.data and hasattr(result.data, "mounts"):
                for mount in result.data.mounts:
                    mounts.append(
                        ShipMount(
                            symbol=getattr(mount, "symbol", "UNKNOWN"),
                            name=getattr(mount, "name", "Unknown Mount"),
                            description=getattr(mount, "description", ""),
                            price=getattr(mount, "price", 0) or 0,
                            mount_type=getattr(mount, "type", "UNKNOWN"),
                        ),
                    )

            return mounts

        except Exception:
            return []

    def purchase_ship(
        self,
        ship_type: str,
        waypoint_symbol: str,
        agent_credits: int,
    ) -> PurchaseResult:
        try:
            result = self._fleet.purchase_ship(
                purchase_request={
                    "ship_type": ship_type,
                    "waypoint_symbol": waypoint_symbol,
                },
            )

            if result.data and result.data.ship:
                ship = result.data.ship
                new_credits = getattr(result.data.agent, "credits", 0) if result.data.agent else agent_credits

                purchase_result = PurchaseResult(
                    success=True,
                    ship_symbol=ship.symbol,
                    price=getattr(ship, "purchase_price", 0) or 0,
                    credits_remaining=new_credits,
                )

                self._purchase_history.append(purchase_result)
                return purchase_result

            return PurchaseResult(success=False, error="No ship returned")

        except Exception as e:
            return PurchaseResult(success=False, error=str(e))

    def can_afford_ship(self, ship_type: str, credits: int) -> bool:
        price = self._ship_prices.get(ship_type, 0)
        return credits >= price

    def get_ship_price(self, ship_type: str) -> int:
        return self._ship_prices.get(ship_type, 0)

    def recommend_ship_for_role(
        self,
        role: str,
        max_price: int | None = None,
    ) -> ShipListing | None:
        candidates = []

        for ships in self._available_ships.values():
            for ship in ships:
                ship_role = SHIP_ROLE_MAP.get(ship.symbol.replace("SHIP_", ""), "transport")
                if ship_role == role:
                    if max_price is None or ship.price <= max_price:
                        candidates.append(ship)

        if not candidates:
            return None

        candidates.sort(key=lambda x: x.price)
        return candidates[0]

    def get_purchase_history(self, limit: int = 20) -> list[dict]:
        history = []
        for result in self._purchase_history[-limit:]:
            history.append(
                {
                    "ship": result.ship_symbol,
                    "price": result.price,
                    "credits_remaining": result.credits_remaining,
                    "success": result.success,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat(),
                },
            )
        return history

    def get_stats(self) -> dict:
        total_spent = sum(r.price for r in self._purchase_history if r.success)
        return {
            "total_purchases": len(self._purchase_history),
            "successful_purchases": sum(1 for r in self._purchase_history if r.success),
            "total_spent": total_spent,
            "ships_available": sum(len(ships) for ships in self._available_ships.values()),
        }


class ShipMaintainer:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api
        self._repair_history: list[dict] = []

    def get_ship_status(self, ship_symbol: str) -> dict | None:
        try:
            result = self._fleet.get_ship(ship_symbol=ship_symbol)
            if not result.data:
                return None

            ship = result.data
            return {
                "symbol": ship.symbol,
                "frame": getattr(ship, "frame", "UNKNOWN"),
                "condition": getattr(ship, "condition", 100),
                "integrity": getattr(ship, "integrity", {}),
                "cargo_capacity": ship.cargo.capacity if ship.cargo else 0,
                "crew": getattr(ship, "crew", {}),
            }

        except Exception:
            return None

    def repair_ship(self, ship_symbol: str) -> dict:
        try:
            result = self._fleet.repair_ship(ship_symbol=ship_symbol)

            if result.data:
                repair_cost = getattr(result.data, "total_damage", 0) or 0
                self._repair_history.append(
                    {
                        "ship": ship_symbol,
                        "cost": repair_cost,
                        "success": True,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                return {"success": True, "ship": ship_symbol, "cost": repair_cost}

            return {"success": False, "ship": ship_symbol, "error": "No data returned"}

        except Exception as e:
            return {"success": False, "ship": ship_symbol, "error": str(e)}

    def scrap_ship(self, ship_symbol: str) -> dict:
        try:
            result = self._fleet.scrap_ship(ship_symbol=ship_symbol)

            if result.data:
                reward = getattr(result.data, "reward", 0) or 0
                self._repair_history.append(
                    {
                        "ship": ship_symbol,
                        "reward": reward,
                        "action": "scrap",
                        "success": True,
                        "timestamp": datetime.now().isoformat(),
                    },
                )
                return {"success": True, "ship": ship_symbol, "reward": reward}

            return {"success": False, "ship": ship_symbol, "error": "No data returned"}

        except Exception as e:
            return {"success": False, "ship": ship_symbol, "error": str(e)}

    def repair_all_miners(self, ship_symbols: list[str]) -> dict:
        results = []
        for symbol in ship_symbols:
            status = self.get_ship_status(symbol)
            if status and status.get("condition", 100) < 100:
                result = self.repair_ship(symbol)
                results.append(result)
            else:
                results.append({"success": True, "ship": symbol, "skipped": True})

        return {
            "repaired": len([r for r in results if r.get("success") and not r.get("skipped")]),
            "skipped": len([r for r in results if r.get("skipped")]),
            "failed": len([r for r in results if not r.get("success") and not r.get("skipped")]),
            "details": results,
        }

    def get_history(self) -> list[dict]:
        return self._repair_history
