from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.core.config import Config
from app.core.fleet_manager import FleetManager, ShipRole, TrackedShip
from app.operations.contract_automation import ContractCoordinator
from app.operations.exploration import ExplorationBot, FleetCoordinator
from app.operations.fleet_builder import FleetExpansionManager
from app.operations.market_db import MarketScanner
from app.operations.mining import GasSiphonBot, MiningBot, RefiningBot
from app.operations.navigation import ConstructionManager, JumpGateNavigator
from app.operations.refining import FuelManager, RefineryBot
from app.operations.shipyard import ShipMaintainer, ShipyardService
from app.operations.trading import CargoManager, TradingBot
from space_traders_api import AgentsApi, ContractsApi, FleetApi, SystemsApi


class FleetBrainState(Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class FleetMetrics:
    total_ships: int = 0
    total_credits: int = 0
    ships_mining: int = 0
    ships_trading: int = 0
    ships_exploring: int = 0
    ships_refining: int = 0
    ships_available: int = 0
    total_cargo_units: int = 0
    total_extracted: int = 0
    total_trades: int = 0
    total_profit: int = 0
    contracts_completed: int = 0
    ships_purchased: int = 0
    credits_spent: int = 0
    fuel_produced: int = 0
    markets_scanned: int = 0


@dataclass
class CycleResults:
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict = field(default_factory=dict)


class FleetBrain:
    def __init__(self):
        config = Config.get_instance()
        api_client = config.get_api_client()

        self._fleet_api = FleetApi(api_client=api_client)
        self._systems_api = SystemsApi(api_client=api_client)
        self._agents_api = AgentsApi(api_client=api_client)
        self._contracts_api = ContractsApi(api_client=api_client)

        self._fleet_manager = FleetManager.get_instance()

        self._mining_bot = MiningBot(self._fleet_api, self._fleet_manager)
        self._trading_bot = TradingBot(self._fleet_api, self._systems_api, self._fleet_manager)
        self._exploration_bot = ExplorationBot(self._fleet_api, self._systems_api, self._fleet_manager)
        self._gas_siphon = GasSiphonBot(self._fleet_api, self._fleet_manager)
        self._refining_bot = RefineryBot(self._fleet_api)

        self._cargo_manager = CargoManager(self._fleet_api)
        self._market_scanner = MarketScanner(self._fleet_api, self._systems_api)
        self._fuel_manager = FuelManager(self._fleet_api)
        self._shipyard = ShipyardService(self._fleet_api, self._systems_api)
        self._ship_maintainer = ShipMaintainer(self._fleet_api)
        self._jump_navigator = JumpGateNavigator(self._fleet_api, self._systems_api)
        self._construction_manager = ConstructionManager(self._fleet_api, self._systems_api)

        self._fleet_coordinator = FleetCoordinator(self._fleet_api, self._fleet_manager)
        self._contract_coord = ContractCoordinator(self._contracts_api, self._fleet_api)
        self._expansion_manager = FleetExpansionManager(self._fleet_api)

        self._state = FleetBrainState.IDLE
        self._metrics = FleetMetrics()
        self._last_metrics_update = datetime.now()
        self._auto_mode = False
        self._cycle_count = 0

    def start(self) -> dict:
        self._state = FleetBrainState.RUNNING
        self._auto_mode = True
        return self._get_status()

    def pause(self) -> dict:
        self._state = FleetBrainState.PAUSED
        return self._get_status()

    def get_status(self) -> dict:
        return self._get_status()

    def _get_status(self) -> dict:
        self._update_metrics()
        return {
            "state": self._state.value,
            "auto_mode": self._auto_mode,
            "cycle_count": self._cycle_count,
            "metrics": {
                "total_ships": self._metrics.total_ships,
                "total_credits": self._metrics.total_credits,
                "ships_mining": self._metrics.ships_mining,
                "ships_trading": self._metrics.ships_trading,
                "ships_exploring": self._metrics.ships_exploring,
                "ships_refining": self._metrics.ships_refining,
                "ships_available": self._metrics.ships_available,
                "total_cargo_units": self._metrics.total_cargo_units,
                "total_extracted": self._metrics.total_extracted,
                "total_trades": self._metrics.total_trades,
                "total_profit": self._metrics.total_profit,
                "contracts_completed": self._metrics.contracts_completed,
                "ships_purchased": self._metrics.ships_purchased,
                "credits_spent": self._metrics.credits_spent,
                "fuel_produced": self._metrics.fuel_produced,
                "markets_scanned": self._metrics.markets_scanned,
            },
            "last_update": self._last_metrics_update.isoformat(),
        }

    def _update_metrics(self) -> None:
        try:
            agent_result = self._agents_api.get_my_agent()
            if agent_result.data:
                self._metrics.total_credits = getattr(agent_result.data, "credits", 0) or 0

            ships_result = self._fleet_api.get_my_ships()
            self._metrics.total_ships = len(ships_result.data) if ships_result.data else 0

            mining_ships = self._fleet_manager.get_ships_by_role(ShipRole.MINING)
            trading_ships = self._fleet_manager.get_ships_by_role(ShipRole.TRADING)
            exploring_ships = self._fleet_manager.get_ships_by_role(ShipRole.EXPLORATION)
            available = self._fleet_manager.get_available_ships()

            self._metrics.ships_mining = len(mining_ships)
            self._metrics.ships_trading = len(trading_ships)
            self._metrics.ships_exploring = len(exploring_ships)
            self._metrics.ships_available = len(available)

            cargo_units = 0
            for ship in ships_result.data or []:
                if ship.cargo:
                    cargo_units += ship.cargo.units or 0
            self._metrics.total_cargo_units = cargo_units

            self._metrics.markets_scanned = len(self._market_scanner.get_db().get_all_markets())

        except Exception:
            pass

        self._last_metrics_update = datetime.now()

    def run_cycle(self) -> dict:
        if self._state != FleetBrainState.RUNNING:
            return {"success": False, "error": f"Brain is {self._state.value}"}

        self._cycle_count += 1

        results = {
            "cycle": self._cycle_count,
            "contracts": self._run_contract_cycle(),
            "mining": self._run_mining_cycle(),
            "refining": self._run_refining_cycle(),
            "trading": self._run_trading_cycle(),
            "exploration": self._run_exploration_cycle(),
            "fuel": self._run_fuel_cycle(),
            "expansion": self._run_expansion_cycle(),
            "market_scan": self._run_market_scan(),
        }

        self._update_metrics()
        return results

    def _run_contract_cycle(self) -> dict:
        self._contract_coord.sync_contracts()
        accepted = self._contract_coord.auto_accept_available()
        fulfilled = self._contract_coord.check_and_fulfill()

        if fulfilled:
            self._metrics.contracts_completed += len(fulfilled)

        return {
            "accepted": len(accepted),
            "fulfilled": len(fulfilled),
        }

    def _run_mining_cycle(self) -> dict:
        mining_ships = self._fleet_manager.get_ships_by_role(ShipRole.MINING)
        results = []
        total_extracted = 0

        for ship in mining_ships[:5]:
            if not ship.is_busy:
                try:
                    result = self._mining_bot.extract(ship)
                    if result:
                        units = result.total_units if hasattr(result, "total_units") else 0
                        total_extracted += units
                        results.append({"ship": ship.symbol, "extracted": units})
                except Exception:
                    pass

        self._metrics.total_extracted += total_extracted

        return {
            "active_miners": len(results),
            "total_extracted": total_extracted,
            "results": results,
        }

    def _run_refining_cycle(self) -> dict:
        refining_ships = self._fleet_manager.get_ships_by_role(ShipRole.REFINING)
        results = []
        total_fuel = 0

        for ship in refining_ships[:3]:
            if not ship.is_busy:
                try:
                    cargo = self._get_ship_cargo(ship.symbol)
                    refinable = self._refining_bot.find_refinable_cargo(cargo)

                    for item in refinable[:2]:
                        recipe = self._refining_bot.get_recipe_for_input(item["symbol"])
                        if recipe:
                            result = self._refining_bot.refine(ship.symbol, recipe.output_symbol, item["units"])
                            if result.success:
                                total_fuel += result.fuel_produced
                                results.append(
                                    {
                                        "ship": ship.symbol,
                                        "input": item["symbol"],
                                        "output": recipe.output_symbol,
                                        "fuel_produced": result.fuel_produced,
                                    }
                                )
                except Exception:
                    pass

        self._metrics.fuel_produced += total_fuel

        return {
            "active_refiners": len(results),
            "total_fuel_produced": total_fuel,
            "results": results,
        }

    def _run_trading_cycle(self) -> dict:
        trading_ships = self._fleet_manager.get_ships_by_role(ShipRole.TRADING)
        opportunities = self._market_scanner.get_trade_opportunities(min_profit=500, min_volume=10)

        return {
            "active_traders": len(trading_ships),
            "opportunities_found": len(opportunities),
            "opportunities": opportunities[:5],
        }

    def _run_exploration_cycle(self) -> dict:
        exploring_ships = self._fleet_manager.get_ships_by_role(ShipRole.EXPLORATION)
        results = []

        for ship in exploring_ships[:2]:
            if not ship.is_busy:
                try:
                    scan_result = self._exploration_bot.scan_system(ship, ship.system or "X1-DF-55")
                    if scan_result:
                        results.append(
                            {
                                "ship": ship.symbol,
                                "waypoints_found": scan_result.waypoints_found,
                                "factions_found": scan_result.factions_found,
                            }
                        )
                except Exception:
                    pass

        return {
            "active_explorers": len(exploring_ships),
            "scans_completed": len(results),
            "results": results,
        }

    def _run_fuel_cycle(self) -> dict:
        ships_needing_fuel = []

        try:
            ships_result = self._fleet_api.get_my_ships()
            for ship_data in ships_result.data or []:
                status = self._fuel_manager.check_fuel_status(ship_data.symbol)
                if status and status.needs_refuel:
                    ships_needing_fuel.append(ship_data.symbol)
        except Exception:
            pass

        refueled_count = 0
        for ship_symbol in ships_needing_fuel[:5]:
            result = self._fuel_manager.refuel_ship(ship_symbol)
            if result.get("success"):
                refueled_count += 1

        return {
            "ships_needing_fuel": len(ships_needing_fuel),
            "refueled": refueled_count,
        }

    def _run_expansion_cycle(self) -> dict:
        if not self._auto_mode:
            return {"skipped": True, "reason": "auto_mode_disabled"}

        try:
            agent_result = self._agents_api.get_my_agent()
            if agent_result.data:
                agent = {
                    "credits": getattr(agent_result.data, "credits", 0) or 0,
                    "headquarters": getattr(agent_result.data, "headquarters", ""),
                }
                if agent["headquarters"]:
                    result = self._expansion_manager.attempt_expansion(
                        agent,
                        agent["headquarters"],
                        target_fleet_size=20,
                    )
                    if result:
                        self._metrics.ships_purchased += 1
                        self._metrics.credits_spent += result.price
                        return {"purchased": result.ship_symbol, "price": result.price}
        except Exception:
            pass

        return {"skipped": False, "purchased": None}

    def _run_market_scan(self) -> dict:
        if not self._market_scanner.get_db().needs_refresh():
            return {"skipped": True, "reason": "cooldown"}

        try:
            agent_result = self._agents_api.get_my_agent()
            if agent_result.data:
                headquarters = getattr(agent_result.data, "headquarters", "")
                if headquarters:
                    system = headquarters.split("-")[0] + "-" + headquarters.split("-")[1]
                    markets = self._market_scanner.scan_system_markets(system)
                    return {"scanned": len(markets), "system": system}
        except Exception:
            pass

        return {"scanned": 0}

    def _get_ship_cargo(self, ship_symbol: str) -> list[dict]:
        try:
            result = self._fleet_api.get_my_ship_cargo(ship_symbol=ship_symbol)
            cargo = []
            if result.data and result.data.inventory:
                for item in result.data.inventory:
                    cargo.append(
                        {
                            "symbol": getattr(item, "symbol", "UNKNOWN"),
                            "units": getattr(item, "units", 0),
                            "name": getattr(item, "name", "Unknown"),
                        }
                    )
            return cargo
        except Exception:
            return []

    def assign_ship_role(self, ship_symbol: str, role: ShipRole) -> dict:
        return self._fleet_coordinator.assign_role(ship_symbol, role)

    def create_mining_fleet(self, num_ships: int = 3) -> dict:
        return self._fleet_coordinator.create_mining_fleet(num_ships)

    def create_trading_fleet(self, num_ships: int = 2) -> dict:
        return self._fleet_coordinator.create_trading_fleet(num_ships)

    def get_fleet_status(self) -> list[dict]:
        ships = []
        try:
            result = self._fleet_api.get_my_ships()
            for ship in result.data or []:
                tracked = self._fleet_manager.get_ship(ship.symbol)
                ships.append(
                    {
                        "symbol": ship.symbol,
                        "role": tracked.role.value if tracked else "unknown",
                        "is_busy": tracked.is_busy if tracked else False,
                        "last_action": tracked.last_action if tracked else None,
                        "cargo_used": ship.cargo.units if ship.cargo else 0,
                        "cargo_capacity": ship.cargo.capacity if ship.cargo else 0,
                        "system": ship.nav.system_symbol if ship.nav else None,
                        "waypoint": ship.nav.waypoint_symbol if ship.nav else None,
                        "status": ship.nav.status.value if ship.nav else "unknown",
                        "fuel": getattr(ship, "fuel", None),
                    },
                )
        except Exception:
            pass
        return ships

    def get_pending_contracts(self) -> list[dict]:
        return self._contract_coord.get_pending_contracts()

    def get_trade_opportunities(self, min_profit: int = 1000) -> list[dict]:
        return self._market_scanner.get_trade_opportunities(min_profit=min_profit, min_volume=10)

    def get_systems(self, system_symbol: str | None = None) -> list[dict]:
        try:
            if system_symbol:
                result = self._systems_api.get_system_waypoints(system_symbol=system_symbol)
            else:
                return []
            waypoints = []
            for wp in result.data or []:
                waypoints.append(
                    {
                        "symbol": wp.symbol,
                        "type": wp.type.value if hasattr(wp.type, "value") else str(wp.type),
                        "x": wp.x,
                        "y": wp.y,
                        "traits": [
                            t.symbol.value if hasattr(t.symbol, "value") else str(t.symbol) for t in (wp.traits or [])
                        ],
                    },
                )
            return waypoints
        except Exception:
            return []

    def navigate_to(self, ship_symbol: str, waypoint: str) -> dict:
        result = self._jump_navigator.navigate_ship(ship_symbol, waypoint)
        return {
            "success": result.success,
            "ship": ship_symbol,
            "destination": waypoint,
            "fuel_consumed": result.fuel_consumed,
            "error": result.error,
        }

    def jump_to_system(self, ship_symbol: str, system: str) -> dict:
        result = self._jump_navigator.jump_ship(ship_symbol, system)
        return {
            "success": result.success,
            "ship": ship_symbol,
            "destination": system,
            "fuel_consumed": result.fuel_consumed,
            "error": result.error,
        }

    def warp_to(self, ship_symbol: str, waypoint: str) -> dict:
        result = self._jump_navigator.warp_ship(ship_symbol, waypoint)
        return {
            "success": result.success,
            "ship": ship_symbol,
            "destination": waypoint,
            "fuel_consumed": result.fuel_consumed,
            "error": result.error,
        }

    def refuel_ship(self, ship_symbol: str) -> dict:
        return self._fuel_manager.refuel_ship(ship_symbol)

    def scan_markets(self, system: str) -> dict:
        markets = self._market_scanner.scan_system_markets(system)
        return {"scanned": len(markets), "markets": [m.waypoint_symbol for m in markets]}

    def get_market_prices(self, waypoint: str) -> dict | None:
        market = self._market_scanner.get_db().get_market(waypoint)
        if not market:
            return None
        return {
            "waypoint": waypoint,
            "system": market.system_symbol,
            "exports": market.exports,
            "imports": market.imports,
            "goods": [
                {
                    "symbol": g.symbol,
                    "name": g.name,
                    "buy_price": g.purchase_price,
                    "sell_price": g.sell_price,
                    "supply": g.supply.value,
                    "activity": g.activity.value,
                }
                for g in market.goods
            ],
        }

    def get_refinery_status(self) -> dict:
        return self._refining_bot.get_stats()

    def get_fuel_status(self, ship_symbol: str) -> dict | None:
        status = self._fuel_manager.check_fuel_status(ship_symbol)
        if not status:
            return None
        return {
            "ship": ship_symbol,
            "current_fuel": status.current_fuel,
            "max_fuel": status.max_fuel,
            "fuel_percent": status.fuel_percent,
            "needs_refuel": status.needs_refuel,
        }

    def get_expansion_stats(self) -> dict:
        return self._expansion_manager.get_expansion_stats()

    def get_navigation_stats(self) -> dict:
        return self._jump_navigator.get_stats()
