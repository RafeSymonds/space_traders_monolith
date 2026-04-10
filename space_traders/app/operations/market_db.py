from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

from space_traders_api import FleetApi, SystemsApi


class SupplyLevel(Enum):
    SCARCE = "SCARCE"
    LIMITED = "LIMITED"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    ABUNDANT = "ABUNDANT"


class MarketActivity(Enum):
    WEAK = "WEAK"
    GROWING = "GROWING"
    STRONG = "STRONG"
    RESTRICTED = "RESTRICTED"


@dataclass
class MarketTradeGood:
    symbol: str
    name: str
    volume: int
    supply: SupplyLevel
    activity: MarketActivity
    purchase_price: int
    sell_price: int
    updated_at: datetime


@dataclass
class WaypointMarket:
    waypoint_symbol: str
    system_symbol: str
    exports: list[str]
    imports: list[str]
    exchange: list[str]
    goods: list[MarketTradeGood]
    updated_at: datetime


@dataclass
class TradeRoute:
    buy_waypoint: str
    sell_waypoint: str
    trade_good: str
    buy_price: int
    sell_price: int
    profit_per_unit: int
    max_volume: int
    estimated_profit: int
    route_efficiency: float
    last_updated: datetime


@dataclass
class PriceHistory:
    symbol: str
    waypoint: str
    buy_price: int
    sell_price: int
    timestamp: datetime


class MarketDatabase:
    def __init__(self):
        self._markets: dict[str, WaypointMarket] = {}
        self._price_history: list[PriceHistory] = []
        self._trade_routes: list[TradeRoute] = []
        self._last_scan = datetime.min
        self._scan_cooldown = timedelta(minutes=5)

    def update_market(self, waypoint: str, system: str, market_data: Any) -> WaypointMarket:
        exports = []
        imports = []
        exchange = []

        if hasattr(market_data, "exports"):
            exports = (
                [e.symbol.value if hasattr(e.symbol, "value") else str(e.symbol) for e in market_data.exports]
                if market_data.exports
                else []
            )
        if hasattr(market_data, "imports"):
            imports = (
                [i.symbol.value if hasattr(i.symbol, "value") else str(i.symbol) for i in market_data.imports]
                if market_data.imports
                else []
            )
        if hasattr(market_data, "exchange"):
            exchange = (
                [e.symbol.value if hasattr(e.symbol, "value") else str(e.symbol) for e in market_data.exchange]
                if market_data.exchange
                else []
            )

        goods = []
        if hasattr(market_data, "trade_goods") and market_data.trade_goods:
            for tg in market_data.trade_goods:
                supply_str = getattr(tg, "supply", "MODERATE")
                try:
                    supply = SupplyLevel(supply_str.value) if hasattr(supply_str, "value") else SupplyLevel(supply_str)
                except ValueError:
                    supply = SupplyLevel.MODERATE

                activity_str = getattr(tg, "activity", "WEAK")
                try:
                    activity = (
                        MarketActivity(activity_str.value)
                        if hasattr(activity_str, "value")
                        else MarketActivity(activity_str)
                    )
                except ValueError:
                    activity = MarketActivity.WEAK

                goods.append(
                    MarketTradeGood(
                        symbol=getattr(tg, "symbol", "UNKNOWN"),
                        name=getattr(tg, "name", "Unknown"),
                        volume=getattr(tg, "trade_volume", 0) or 0,
                        supply=supply,
                        activity=activity,
                        purchase_price=getattr(tg, "purchase_price", 0) or 0,
                        sell_price=getattr(tg, "sell_price", 0) or 0,
                        updated_at=datetime.now(),
                    ),
                )

        market = WaypointMarket(
            waypoint_symbol=waypoint,
            system_symbol=system,
            exports=exports,
            imports=imports,
            exchange=exchange,
            goods=goods,
            updated_at=datetime.now(),
        )

        self._markets[waypoint] = market
        self._update_price_history(waypoint, goods)

        return market

    def _update_price_history(self, waypoint: str, goods: list[MarketTradeGood]) -> None:
        for good in goods:
            self._price_history.append(
                PriceHistory(
                    symbol=good.symbol,
                    waypoint=waypoint,
                    buy_price=good.purchase_price,
                    sell_price=good.sell_price,
                    timestamp=datetime.now(),
                ),
            )
        if len(self._price_history) > 10000:
            self._price_history = self._price_history[-5000:]

    def get_market(self, waypoint: str) -> WaypointMarket | None:
        return self._markets.get(waypoint)

    def get_good_price(self, waypoint: str, good_symbol: str) -> tuple[int, int] | None:
        market = self._markets.get(waypoint)
        if not market:
            return None

        for good in market.goods:
            if good.symbol == good_symbol:
                return (good.purchase_price, good.sell_price)

        return None

    def find_best_route(
        self,
        good_symbol: str,
        min_profit: int = 100,
        max_routes: int = 10,
    ) -> list[TradeRoute]:
        routes = []
        markets = list(self._markets.values())

        for buy_market in markets:
            for sell_market in markets:
                if buy_market.waypoint_symbol == sell_market.waypoint_symbol:
                    continue

                buy_price = None
                sell_price = None
                max_volume = 0

                for good in buy_market.goods:
                    if good.symbol == good_symbol:
                        buy_price = good.purchase_price
                        max_volume = good.volume
                        break

                if buy_price is None or buy_price == 0:
                    continue

                for good in sell_market.goods:
                    if good.symbol == good_symbol:
                        sell_price = good.sell_price
                        max_volume = min(max_volume, good.volume)
                        break

                if sell_price is None or sell_price == 0:
                    continue

                profit = sell_price - buy_price
                if profit < min_profit:
                    continue

                estimated_profit = profit * max_volume
                efficiency = (profit / buy_price * 100) if buy_price > 0 else 0

                routes.append(
                    TradeRoute(
                        buy_waypoint=buy_market.waypoint_symbol,
                        sell_waypoint=sell_market.waypoint_symbol,
                        trade_good=good_symbol,
                        buy_price=buy_price,
                        sell_price=sell_price,
                        profit_per_unit=profit,
                        max_volume=max_volume,
                        estimated_profit=estimated_profit,
                        route_efficiency=efficiency,
                        last_updated=datetime.now(),
                    ),
                )

        routes.sort(key=lambda x: x.estimated_profit, reverse=True)
        self._trade_routes = routes[:max_routes]
        return self._trade_routes

    def get_market_comparison(self, good_symbol: str) -> list[dict]:
        comparison = []
        for waypoint, market in self._markets.items():
            for good in market.goods:
                if good.symbol == good_symbol:
                    comparison.append(
                        {
                            "waypoint": waypoint,
                            "system": market.system_symbol,
                            "buy_price": good.purchase_price,
                            "sell_price": good.sell_price,
                            "profit": good.sell_price - good.purchase_price,
                            "supply": good.supply.value,
                            "activity": good.activity.value,
                            "volume": good.volume,
                        },
                    )
        comparison.sort(key=lambda x: x["profit"], reverse=True)
        return comparison

    def needs_refresh(self) -> bool:
        return datetime.now() - self._last_scan > self._scan_cooldown

    def mark_scanned(self) -> None:
        self._last_scan = datetime.now()

    def get_all_markets(self) -> list[WaypointMarket]:
        return list(self._markets.values())

    def get_routes(self) -> list[TradeRoute]:
        return self._trade_routes

    def get_stats(self) -> dict:
        return {
            "markets_cached": len(self._markets),
            "price_history_entries": len(self._price_history),
            "active_routes": len(self._trade_routes),
            "last_scan": self._last_scan.isoformat(),
        }


class MarketScanner:
    def __init__(self, fleet_api: FleetApi, systems_api: SystemsApi):
        self._fleet = fleet_api
        self._systems = systems_api
        self._db = MarketDatabase()

    def get_db(self) -> MarketDatabase:
        return self._db

    def scan_market(self, system_symbol: str, waypoint_symbol: str) -> WaypointMarket | None:
        try:
            result = self._systems.get_market(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )

            if result.data:
                market_data = result.data
                return self._db.update_market(waypoint_symbol, system_symbol, market_data)

        except Exception:
            pass

        return None

    def scan_system_markets(
        self,
        system_symbol: str,
        waypoints_filter: list[str] | None = None,
    ) -> list[WaypointMarket]:
        markets = []
        try:
            result = self._systems.get_system_waypoints(system_symbol=system_symbol)

            for wp in result.data or []:
                waypoint_symbol = wp.symbol
                has_market = False

                if wp.traits:
                    for trait in wp.traits:
                        trait_symbol = trait.symbol.value if hasattr(trait.symbol, "value") else str(trait.symbol)
                        if trait_symbol == "MARKETPLACE":
                            has_market = True
                            break

                if not has_market:
                    continue

                if waypoints_filter and waypoint_symbol not in waypoints_filter:
                    continue

                market = self.scan_market(system_symbol, waypoint_symbol)
                if market:
                    markets.append(market)

            self._db.mark_scanned()

        except Exception:
            pass

        return markets

    def find_trade_routes(
        self,
        good_symbol: str | None = None,
        min_profit: int = 100,
    ) -> list[TradeRoute]:
        if good_symbol:
            return self._db.find_best_route(good_symbol, min_profit=min_profit)

        all_routes = []
        tracked_goods = set()

        for market in self._db.get_all_markets():
            for good in market.goods:
                if good.symbol not in tracked_goods:
                    tracked_goods.add(good.symbol)
                    routes = self._db.find_best_route(good.symbol, min_profit=min_profit)
                    all_routes.extend(routes)

        all_routes.sort(key=lambda x: x.estimated_profit, reverse=True)
        return all_routes[:20]

    def get_trade_opportunities(
        self,
        min_profit: int = 500,
        min_volume: int = 10,
    ) -> list[dict]:
        routes = self.find_trade_routes(min_profit=min_profit)
        opportunities = []

        for route in routes:
            if route.max_volume >= min_volume:
                opportunities.append(
                    {
                        "buy_location": route.buy_waypoint,
                        "sell_location": route.sell_waypoint,
                        "trade_good": route.trade_good,
                        "buy_price": route.buy_price,
                        "sell_price": route.sell_price,
                        "profit_per_unit": route.profit_per_unit,
                        "volume": route.max_volume,
                        "total_profit": route.estimated_profit,
                        "efficiency": route.route_efficiency,
                    },
                )

        return opportunities

    def find_mining_markets(self) -> list[dict]:
        mining_locations = []
        for market in self._db.get_all_markets():
            for good in market.goods:
                if "_ORE" in good.symbol or "_CRYSTALS" in good.symbol or "_SAND" in good.symbol:
                    if good.supply in [SupplyLevel.SCARCE, SupplyLevel.LIMITED]:
                        mining_locations.append(
                            {
                                "waypoint": market.waypoint_symbol,
                                "system": market.system_symbol,
                                "resource": good.symbol,
                                "price": good.sell_price,
                                "supply": good.supply.value,
                                "demand": "HIGH" if good.supply == SupplyLevel.SCARCE else "MODERATE",
                            },
                        )
        return mining_locations

    def find_selling_markets(self, resource: str) -> list[dict]:
        selling_markets = []
        for market in self._db.get_all_markets():
            for good in market.goods:
                if good.symbol == resource:
                    if resource in market.imports or resource in market.exchange:
                        selling_markets.append(
                            {
                                "waypoint": market.waypoint_symbol,
                                "system": market.system_symbol,
                                "buy_price": good.purchase_price,
                                "sell_price": good.sell_price,
                                "supply": good.supply.value,
                            },
                        )
        selling_markets.sort(key=lambda x: x["buy_price"], reverse=True)
        return selling_markets
