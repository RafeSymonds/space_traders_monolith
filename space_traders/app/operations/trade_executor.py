from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from app.core.fleet_manager import FleetManager, ShipRole, TrackedShip
from app.operations.market_db import MarketDatabase, TradeRoute, WaypointMarket
from app.operations.ship_navigator import ShipNavigator, ShipActivity
from space_traders_api import FleetApi


class TradeExecutionState(Enum):
    IDLE = "idle"
    NAVIGATING_TO_BUY = "navigating_to_buy"
    BUYING = "buying"
    NAVIGATING_TO_SELL = "navigating_to_sell"
    SELLING = "selling"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TradeExecution:
    trade_route: TradeRoute
    ship_symbol: str
    quantity: int
    state: TradeExecutionState = TradeExecutionState.IDLE
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None
    buy_cost: int = 0
    sell_revenue: int = 0
    fuel_cost: int = 0
    profit: int = 0
    error: str | None = None


@dataclass
class MultiHopRoute:
    stops: list[str]
    goods: list[str]
    total_profit: int
    estimated_time_minutes: int
    legs: list[dict]


@dataclass  
class TradeScore:
    route: TradeRoute
    score: float
    profit_per_hour: float
    efficiency: float
    risk_factor: float


class ProfitCalculator:
    FUEL_COST_PER_DISTANCE = 1
    TIME_COST_PER_MINUTE = 10

    @staticmethod
    def calculate_true_profit(
        route: TradeRoute,
        ship_capacity: int,
        fuel_cost: int = 0,
        time_minutes: int = 0,
    ) -> dict:
        max_units = min(route.max_volume, ship_capacity)
        gross_profit = route.profit_per_unit * max_units
        net_profit = gross_profit - fuel_cost - (time_minutes * ProfitCalculator.TIME_COST_PER_MINUTE)
        roi = (net_profit / (route.buy_price * max_units)) * 100 if route.buy_price > 0 and max_units > 0 else 0
        
        return {
            "max_units": max_units,
            "gross_profit": gross_profit,
            "fuel_cost": fuel_cost,
            "time_cost": time_minutes * ProfitCalculator.TIME_COST_PER_MINUTE,
            "net_profit": net_profit,
            "roi_percent": roi,
            "profit_per_hour": net_profit / max(1, time_minutes / 60),
        }

    @staticmethod
    def estimate_fuel_cost(distance: float, ship_size: str = "MEDIUM") -> int:
        size_multiplier = {"SMALL": 0.5, "MEDIUM": 1.0, "LARGE": 2.0}.get(ship_size, 1.0)
        return int(distance * ProfitCalculator.FUEL_COST_PER_DISTANCE * size_multiplier)

    @staticmethod
    def estimate_time(distance: float, speed: str = "FAST") -> int:
        speed_map = {"SLOW": 120, "NORMAL": 60, "FAST": 30, "VERY_FAST": 15}
        base_seconds = speed_map.get(speed, 60)
        return int(distance * base_seconds / 60)


class SmartTradeExecutor:
    def __init__(
        self,
        fleet_api: FleetApi,
        fleet_manager: FleetManager,
        market_db: MarketDatabase,
        navigator: ShipNavigator,
    ):
        self._fleet = fleet_api
        self._fleet_manager = fleet_manager
        self._market_db = market_db
        self._navigator = navigator
        self._active_trades: dict[str, TradeExecution] = {}
        self._trade_history: list[TradeExecution] = []

    def execute_trade(
        self,
        route: TradeRoute,
        ship_symbol: str,
        quantity: int | None = None,
    ) -> TradeExecution:
        execution = TradeExecution(
            trade_route=route,
            ship_symbol=ship_symbol,
            quantity=quantity or route.max_volume,
            state=TradeExecutionState.NAVIGATING_TO_BUY,
        )
        self._active_trades[ship_symbol] = execution
        return execution

    def tick_trade(self, ship_symbol: str) -> dict:
        execution = self._active_trades.get(ship_symbol)
        if not execution:
            return {"done": True, "error": "No active trade"}

        ship = self._fleet_manager.get_ship(ship_symbol)
        if not ship:
            return {"done": True, "error": "Ship not found"}

        nav_state = self._navigator.get_state(ship_symbol)

        if execution.state == TradeExecutionState.NAVIGATING_TO_BUY:
            if nav_state.is_traveling():
                return {"done": False, "state": "en_route_to_buy", "destination": execution.trade_route.buy_waypoint}
            
            self._do_buy(execution, ship)
            return {"done": False, "state": "bought", "quantity": execution.quantity}

        elif execution.state == TradeExecutionState.BUYING:
            return {"done": False, "state": "buying"}

        elif execution.state == TradeExecutionState.NAVIGATING_TO_SELL:
            if nav_state.is_traveling():
                return {"done": False, "state": "en_route_to_sell", "destination": execution.trade_route.sell_waypoint}
            
            self._do_sell(execution, ship)
            return {"done": False, "state": "sold"}

        elif execution.state == TradeExecutionState.SELLING:
            return {"done": False, "state": "selling"}

        elif execution.state == TradeExecutionState.COMPLETED:
            return self._finalize_trade(execution)

        return {"done": True, "error": "Unknown state"}

    def _do_buy(self, execution: TradeExecution, ship: TrackedShip) -> None:
        execution.state = TradeExecutionState.BUYING
        try:
            result = self._fleet.purchase_cargo(
                ship_symbol=ship_symbol=execution.ship_symbol,
                purchase_request={
                    "trade_symbol": execution.trade_route.trade_good,
                    "units": execution.quantity,
                },
            )
            if result.data:
                execution.buy_cost = execution.quantity * execution.trade_route.buy_price
                execution.state = TradeExecutionState.NAVIGATING_TO_SELL
                self._navigator.navigate_ship(
                    ship,
                    execution.trade_route.sell_waypoint,
                    estimated_seconds=60,
                )
        except Exception as e:
            execution.state = TradeExecutionState.FAILED
            execution.error = str(e)

    def _do_sell(self, execution: TradeExecution, ship: TrackedShip) -> None:
        execution.state = TradeExecutionState.SELLING
        try:
            result = self._fleet.sell_cargo(
                ship_symbol=execution.ship_symbol,
                sell_request={
                    "trade_symbol": execution.trade_route.trade_good,
                    "units": execution.quantity,
                },
            )
            if result.data:
                execution.sell_revenue = result.data.transaction.total_price
                execution.profit = execution.sell_revenue - execution.buy_cost - execution.fuel_cost
                execution.state = TradeExecutionState.COMPLETED
                execution.completed_at = datetime.now()
        except Exception as e:
            execution.state = TradeExecutionState.FAILED
            execution.error = str(e)

    def _finalize_trade(self, execution: TradeExecution) -> dict:
        result = {
            "done": True,
            "success": execution.state == TradeExecutionState.COMPLETED,
            "ship": execution.ship_symbol,
            "good": execution.trade_route.trade_good,
            "quantity": execution.quantity,
            "buy_cost": execution.buy_cost,
            "sell_revenue": execution.sell_revenue,
            "profit": execution.profit,
            "duration_seconds": (execution.completed_at - execution.started_at).total_seconds(),
        }
        self._trade_history.append(execution)
        del self._active_trades[execution.ship_symbol]
        return result

    def get_active_trade(self, ship_symbol: str) -> TradeExecution | None:
        return self._active_trades.get(ship_symbol)

    def get_trade_history(self, limit: int = 100) -> list[dict]:
        return [
            {
                "ship": e.ship_symbol,
                "good": e.trade_route.trade_good,
                "profit": e.profit,
                "completed_at": e.completed_at.isoformat() if e.completed_at else None,
            }
            for e in self._trade_history[-limit:]
        ]

    def get_total_profit(self) -> int:
        return sum(e.profit for e in self._trade_history if e.profit > 0)


class MultiHopRoutePlanner:
    def __init__(self, market_db: MarketDatabase):
        self._market_db = market_db

    def find_multi_hop_routes(
        self,
        start_waypoint: str,
        max_hops: int = 3,
        min_profit: int = 500,
    ) -> list[MultiHopRoute]:
        routes = []
        markets = self._market_db.get_all_markets()

        for market in markets:
            first_routes = self._find_routes_from_market(market, min_profit)
            for route in first_routes:
                chain = self._extend_route(route, max_hops - 1, min_profit)
                if chain and len(chain.stops) >= 2:
                    routes.append(chain)

        routes.sort(key=lambda x: x.total_profit, reverse=True)
        return routes[:10]

    def _find_routes_from_market(
        self,
        market: WaypointMarket,
        min_profit: int,
    ) -> list[TradeRoute]:
        routes = []
        for good in market.goods:
            if good.purchase_price > 0:
                routes.extend(self._market_db.find_best_route(good.symbol, min_profit))
        return routes

    def _extend_route(
        self,
        start_route: TradeRoute,
        remaining_hops: int,
        min_profit: int,
    ) -> MultiHopRoute | None:
        stops = [start_route.buy_waypoint, start_route.sell_waypoint]
        goods = [start_route.trade_good]
        total_profit = start_route.estimated_profit
        legs = [{
            "from": start_route.buy_waypoint,
            "to": start_route.sell_waypoint,
            "good": start_route.trade_good,
            "profit": start_route.estimated_profit,
        }]

        last_market = self._market_db.get_market(start_route.sell_waypoint)
        if not last_market or remaining_hops <= 0:
            return MultiHopRoute(
                stops=stops,
                goods=goods,
                total_profit=total_profit,
                estimated_time_minutes=len(stops) * 5,
                legs=legs,
            )

        next_routes = self._find_routes_from_market(last_market, min_profit)
        next_routes = [r for r in next_routes if r.sell_waypoint not in stops]

        if not next_routes:
            return MultiHopRoute(
                stops=stops,
                goods=goods,
                total_profit=total_profit,
                estimated_time_minutes=len(stops) * 5,
                legs=legs,
            )

        best_next = next_routes[0]
        stops.append(best_next.sell_waypoint)
        goods.append(best_next.trade_good)
        total_profit += best_next.estimated_profit
        legs.append({
            "from": best_next.buy_waypoint,
            "to": best_next.sell_waypoint,
            "good": best_next.trade_good,
            "profit": best_next.estimated_profit,
        })

        return MultiHopRoute(
            stops=stops,
            goods=goods,
            total_profit=total_profit,
            estimated_time_minutes=len(stops) * 5,
            legs=legs,
        )

    def score_routes(self, routes: list[MultiHopRoute], ship_capacity: int) -> list[TradeScore]:
        scored = []
        for route in routes:
            profit_data = ProfitCalculator.calculate_true_profit(
                route=TradeRoute(
                    buy_waypoint=route.stops[0],
                    sell_waypoint=route.stops[-1],
                    trade_good=route.goods[0],
                    buy_price=0,
                    sell_price=0,
                    profit_per_unit=route.total_profit // max(1, ship_capacity),
                    max_volume=ship_capacity,
                    estimated_profit=route.total_profit,
                    route_efficiency=0,
                    last_updated=datetime.now(),
                ),
                ship_capacity=ship_capacity,
            )
            
            score = TradeScore(
                route=TradeRoute(
                    buy_waypoint=route.stops[0],
                    sell_waypoint=route.stops[-1],
                    trade_good=route.goods[0],
                    buy_price=0,
                    sell_price=0,
                    profit_per_unit=route.total_profit // max(1, ship_capacity),
                    max_volume=ship_capacity,
                    estimated_profit=route.total_profit,
                    route_efficiency=0,
                    last_updated=datetime.now(),
                ),
                score=profit_data["net_profit"],
                profit_per_hour=profit_data["profit_per_hour"],
                efficiency=profit_data["roi_percent"],
                risk_factor=1.0 / len(route.stops),
            )
            scored.append(score)

        scored.sort(key=lambda x: x.score, reverse=True)
        return scored