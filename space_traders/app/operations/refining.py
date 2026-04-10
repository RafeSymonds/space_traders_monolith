from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from space_traders_api import FleetApi


class RefineryState(Enum):
    IDLE = "idle"
    REFINING = "refining"
    COOLDOWN = "cooldown"
    ERROR = "error"


@dataclass
class RefiningResult:
    success: bool
    ship_symbol: str
    produced: list[dict]
    consumed: list[dict]
    fuel_produced: int = 0
    error: str | None = None
    cooldown_remaining: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FuelStatus:
    ship_symbol: str
    current_fuel: int
    max_fuel: int
    fuel_percent: float
    needs_refuel: bool
    estimated_cost: int | None = None


@dataclass
class RefineryRecipe:
    input_symbol: str
    output_symbol: str
    output_units: int
    refine_time: int


KNOWN_RECIPES = [
    RefineryRecipe("IRON_ORE", "IRON", 10, 60),
    RefineryRecipe("COPPER_ORE", "COPPER", 10, 60),
    RefineryRecipe("SILVER_ORE", "SILVER", 10, 60),
    RefineryRecipe("GOLD_ORE", "GOLD", 10, 60),
    RefineryRecipe("ALUMINUM_ORE", "ALUMINUM", 10, 60),
    RefineryRecipe("PLATINUM_ORE", "PLATINUM", 10, 60),
    RefineryRecipe("URANITE_ORE", "URANIUM", 10, 60),
    RefineryRecipe("MERITIUM_ORE", "MERITIUM", 10, 60),
    RefineryRecipe("REACTOR_FUEL", "FUEL", 100, 120),
]


class RefineryBot:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api
        self._refining_history: list[RefiningResult] = []
        self._cooldowns: dict[str, datetime] = {}

    def refine(
        self,
        ship_symbol: str,
        produce_symbol: str,
        units: int = 1,
    ) -> RefiningResult:
        if self._is_on_cooldown(ship_symbol):
            cooldown = self._get_cooldown_remaining(ship_symbol)
            return RefiningResult(
                success=False,
                ship_symbol=ship_symbol,
                produced=[],
                consumed=[],
                error=f"Ship on cooldown: {cooldown}s remaining",
                cooldown_remaining=cooldown,
            )

        recipe = self.get_recipe_for_input(produce_symbol)
        output_multiplier = recipe.output_units if recipe else units

        try:
            result = self._fleet.ship_refine(
                ship_symbol=ship_symbol,
                ship_refine_request={
                    "produce": produce_symbol,
                    "units": units,
                },
            )

            produced = []
            consumed = []

            if result.data and result.data.produced:
                for item in result.data.produced:
                    produced.append(
                        {
                            "symbol": getattr(item, "trade_symbol", "UNKNOWN"),
                            "units": getattr(item, "units", 0),
                        },
                    )

            if result.data and result.data.consumed:
                for item in result.data.consumed:
                    consumed.append(
                        {
                            "symbol": getattr(item, "trade_symbol", "UNKNOWN"),
                            "units": getattr(item, "units", 0),
                        },
                    )

            fuel_produced = 0
            if produce_symbol == "FUEL":
                fuel_produced = units

            refining_result = RefiningResult(
                success=True,
                ship_symbol=ship_symbol,
                produced=produced,
                consumed=consumed,
                fuel_produced=fuel_produced,
            )

            self._refining_history.append(refining_result)
            self._set_cooldown(ship_symbol, timedelta(seconds=60))

            return refining_result

        except Exception as e:
            return RefiningResult(
                success=False,
                ship_symbol=ship_symbol,
                produced=[],
                consumed=[],
                error=str(e),
            )

    def auto_refine_for_fuel(
        self,
        ship_symbol: str,
        available_cargo: list[dict],
    ) -> RefiningResult:
        reactor_fuel = next((item for item in available_cargo if item.get("symbol") == "REACTOR_FUEL"), None)

        if not reactor_fuel:
            return RefiningResult(
                success=False,
                ship_symbol=ship_symbol,
                produced=[],
                consumed=[],
                error="No REACTOR_FUEL in cargo to refine",
            )

        units_to_refine = min(reactor_fuel.get("units", 0), 10)

        return self.refine(ship_symbol, "FUEL", units_to_refine)

    def get_recipe_for_input(self, input_symbol: str) -> RefineryRecipe | None:
        for recipe in KNOWN_RECIPES:
            if recipe.input_symbol == input_symbol:
                return recipe
        return None

    def find_refinable_cargo(self, cargo: list[dict]) -> list[dict]:
        refinable = []
        for item in cargo:
            if self.get_recipe_for_input(item.get("symbol", "")):
                refinable.append(item)
        return refinable

    def _is_on_cooldown(self, ship_symbol: str) -> bool:
        if ship_symbol not in self._cooldowns:
            return False
        return datetime.now() < self._cooldowns[ship_symbol]

    def _get_cooldown_remaining(self, ship_symbol: str) -> int:
        if ship_symbol not in self._cooldowns:
            return 0
        remaining = self._cooldowns[ship_symbol] - datetime.now()
        return max(0, int(remaining.total_seconds()))

    def _set_cooldown(self, ship_symbol: str, duration: timedelta) -> None:
        self._cooldowns[ship_symbol] = datetime.now() + duration

    def get_cooldown(self, ship_symbol: str) -> int:
        return self._get_cooldown_remaining(ship_symbol)

    def get_history(self, limit: int = 50) -> list[dict]:
        history = []
        for result in self._refining_history[-limit:]:
            history.append(
                {
                    "success": result.success,
                    "ship": result.ship_symbol,
                    "produced": result.produced,
                    "consumed": result.consumed,
                    "fuel_produced": result.fuel_produced,
                    "error": result.error,
                    "timestamp": result.timestamp.isoformat(),
                },
            )
        return history

    def get_stats(self) -> dict:
        total_refined = len(self._refining_history)
        successful = sum(1 for r in self._refining_history if r.success)
        total_fuel_produced = sum(r.fuel_produced for r in self._refining_history)

        return {
            "total_refines": total_refined,
            "successful": successful,
            "failed": total_refined - successful,
            "total_fuel_produced": total_fuel_produced,
            "success_rate": (successful / total_refined * 100) if total_refined > 0 else 0,
        }


class FuelManager:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api
        self._refinery_bot = RefineryBot(fleet_api)
        self._fuel_reserves: dict[str, int] = {}

    def get_refinery_bot(self) -> RefineryBot:
        return self._refinery_bot

    def check_fuel_status(self, ship_symbol: str) -> FuelStatus | None:
        try:
            result = self._fleet.get_my_ship(ship_symbol=ship_symbol)
            if not result.data:
                return None

            ship = result.data
            fuel = getattr(ship, "fuel", None)
            if not fuel:
                return FuelStatus(
                    ship_symbol=ship_symbol,
                    current_fuel=0,
                    max_fuel=100,
                    fuel_percent=0,
                    needs_refuel=True,
                )

            current = getattr(fuel, "current", 0) or 0
            capacity = getattr(fuel, "capacity", 100) or 100
            percent = (current / capacity * 100) if capacity > 0 else 0

            needs_refuel = percent < 50

            return FuelStatus(
                ship_symbol=ship_symbol,
                current_fuel=current,
                max_fuel=capacity,
                fuel_percent=percent,
                needs_refuel=needs_refuel,
            )

        except Exception:
            return None

    def refuel_ship(
        self,
        ship_symbol: str,
        units: int | None = None,
        use_cargo_fuel: bool = True,
    ) -> dict:
        try:
            if units is not None:
                result = self._fleet.refuel_ship(
                    ship_symbol=ship_symbol,
                    refuel_ship_request={"units": units},
                )
            else:
                result = self._fleet.refuel_ship(ship_symbol=ship_symbol)

            if result.data and result.data.agent:
                new_fuel = result.data.agent
                return {
                    "success": True,
                    "ship": ship_symbol,
                    "new_fuel": getattr(new_fuel, "credits", None),
                }

            return {"success": True, "ship": ship_symbol}

        except Exception as e:
            return {"success": False, "ship": ship_symbol, "error": str(e)}

    def refuel_all_miners(
        self,
        ship_symbols: list[str],
        min_fuel_percent: float = 50,
    ) -> dict:
        results = []
        for symbol in ship_symbols:
            status = self.check_fuel_status(symbol)
            if status and status.needs_refuel:
                result = self.refuel_ship(symbol)
                results.append(result)
            else:
                results.append({"success": True, "ship": symbol, "skipped": True})

        return {
            "refueled": len([r for r in results if r.get("success") and not r.get("skipped")]),
            "skipped": len([r for r in results if r.get("skipped")]),
            "failed": len([r for r in results if not r.get("success") and not r.get("skipped")]),
            "details": results,
        }

    def add_fuel_reserve(self, system_waypoint: str, amount: int) -> None:
        self._fuel_reserves[system_waypoint] = self._fuel_reserves.get(system_waypoint, 0) + amount

    def get_fuel_reserve(self, system_waypoint: str) -> int:
        return self._fuel_reserves.get(system_waypoint, 0)

    def get_all_reserves(self) -> dict[str, int]:
        return self._fuel_reserves.copy()
