from dataclasses import dataclass

from app.core.fleet_manager import FleetManager, TrackedShip
from space_traders_api import FleetApi, SystemsApi


@dataclass
class ExtractionResult:
    ship_symbol: str
    extracts: list[str]
    total_units: int


@dataclass
class TradeOpportunity:
    good: str
    buy_price: int
    sell_price: int
    profit_per_unit: int
    waypoint: str


class MiningOperations:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api

    async def extract(
        self,
        ship: TrackedShip,
        surveys: list | None = None,
        duration_seconds: int = 60,
    ) -> ExtractionResult:
        ship.is_busy = True
        ship.last_action = "extracting"
        try:
            if surveys:
                result = self._fleet.extract_resources_with_survey(
                    ship_symbol=ship.symbol,
                    survey=surveys[0],
                )
            else:
                result = self._fleet.extract_resources(ship_symbol=ship.symbol)

            extracts = []
            total_units = 0
            if result.data and result.data.extraction:
                yields = result.data.extraction.yield_
                for y in yields:
                    extracts.append(f"{y.symbol}: {y.units}")
                    total_units += y.units

            return ExtractionResult(
                ship_symbol=ship.symbol,
                extracts=extracts,
                total_units=total_units,
            )
        finally:
            ship.is_busy = False

    async def survey(self, ship: TrackedShip) -> list:
        ship.is_busy = True
        ship.last_action = "surveying"
        try:
            result = self._fleet.create_survey(ship_symbol=ship.symbol)
            return result.data.surveys if result.data else []
        finally:
            ship.is_busy = False


class TradingOperations:
    def __init__(self, fleet_api: FleetApi, systems_api: SystemsApi):
        self._fleet = fleet_api
        self._systems = systems_api

    async def find_best_trades(
        self,
        system: str,
        min_profit: int = 1000,
    ) -> list[TradeOpportunity]:
        opportunities = []
        return opportunities

    async def purchase(
        self,
        ship: TrackedShip,
        good: str,
        quantity: int,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = "purchasing"
        try:
            result = self._fleet.purchase_cargo(
                ship_symbol=ship.symbol,
                trade_symbol=good,
                units=quantity,
            )
            return {
                "success": True,
                "ship": ship.symbol,
                "purchased": f"{good} x{quantity}",
                "total_price": result.data.transaction.total_price if result.data else 0,
            }
        finally:
            ship.is_busy = False

    async def sell(
        self,
        ship: TrackedShip,
        good: str,
        quantity: int,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = "selling"
        try:
            result = self._fleet.sell_cargo(
                ship_symbol=ship.symbol,
                trade_symbol=good,
                units=quantity,
            )
            return {
                "success": True,
                "ship": ship.symbol,
                "sold": f"{good} x{quantity}",
                "total_price": result.data.transaction.total_price if result.data else 0,
            }
        finally:
            ship.is_busy = False


class NavigationOperations:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api

    async def dock(self, ship: TrackedShip) -> dict:
        ship.is_busy = True
        ship.last_action = "docking"
        try:
            result = self._fleet.dock_ship(ship_symbol=ship.symbol)
            return {"success": True, "ship": ship.symbol, "status": "docked"}
        finally:
            ship.is_busy = False

    async def orbit(self, ship: TrackedShip) -> dict:
        ship.is_busy = True
        ship.last_action = "orbiting"
        try:
            result = self._fleet.orbit_ship(ship_symbol=ship.symbol)
            return {"success": True, "ship": ship.symbol, "status": "orbiting"}
        finally:
            ship.is_busy = False

    async def navigate(
        self,
        ship: TrackedShip,
        waypoint: str,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = f"navigating to {waypoint}"
        try:
            result = self._fleet.navigate_ship(
                ship_symbol=ship.symbol,
                waypoint_symbol=waypoint,
            )
            return {
                "success": True,
                "ship": ship.symbol,
                "destination": waypoint,
                "arrival": result.data.nav.status if result.data else "unknown",
            }
        finally:
            ship.is_busy = False

    async def jump(
        self,
        ship: TrackedShip,
        system: str,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = f"jumping to {system}"
        try:
            result = self._fleet.jump_ship(
                ship_symbol=ship.symbol,
                system_symbol=system,
            )
            return {
                "success": True,
                "ship": ship.symbol,
                "destination": system,
            }
        finally:
            ship.is_busy = False

    async def warp(
        self,
        ship: TrackedShip,
        system: str,
        waypoint: str,
    ) -> dict:
        ship.is_busy = True
        ship.last_action = f"warping to {waypoint}"
        try:
            await self.orbit(ship)
            result = self._fleet.warp_ship(
                ship_symbol=ship.symbol,
                waypoint_symbol=waypoint,
            )
            return {
                "success": True,
                "ship": ship.symbol,
                "destination": waypoint,
            }
        finally:
            ship.is_busy = False


class FleetOperations:
    def __init__(
        self,
        fleet_api: FleetApi,
        mining: MiningOperations,
        trading: TradingOperations,
        navigation: NavigationOperations,
    ):
        self._fleet = fleet_api
        self._mining = mining
        self._trading = trading
        self._navigation = navigation
        self._fleet_manager = FleetManager.get_instance()

    async def status(self) -> dict:
        await self._fleet_manager.refresh_all_ships()
        ships = []
        for symbol, tracked in self._fleet_manager.ships.items():
            ships.append(
                {
                    "symbol": symbol,
                    "role": tracked.role.value,
                    "system": tracked.system,
                    "waypoint": tracked.current_waypoint,
                    "busy": tracked.is_busy,
                    "last_action": tracked.last_action,
                    "cargo": {
                        "used": tracked.cargo_used,
                        "capacity": tracked.cargo_capacity,
                    },
                },
            )
        return {"fleet": ships, "total_ships": len(ships)}
