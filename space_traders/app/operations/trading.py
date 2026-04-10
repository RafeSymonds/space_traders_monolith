from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.core.fleet_manager import FleetManager, TrackedShip
from space_traders_api import FleetApi, SystemsApi


class SupplyLevel(Enum):
    SCARCE = "SCARCE"
    LIMITED = "LIMITED"
    MODERATE = "MODERATE"
    ABUNDANT = "ABUNDANT"


class TradeAction(Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class MarketPrice:
    good: str
    symbol: str
    purchase_price: int
    sell_price: int
    supply: SupplyLevel
    trade_volume: int


@dataclass
class TradeOpportunity:
    buy_market: str
    sell_market: str
    good: str
    buy_price: int
    sell_price: int
    profit_per_unit: int
    max_units: int
    expected_profit: int

    @property
    def margin(self) -> float:
        if self.buy_price == 0:
            return 0.0
        return (self.sell_price - self.buy_price) / self.buy_price


@dataclass
class TradeResult:
    timestamp: datetime
    ship_symbol: str
    action: TradeAction
    good: str
    quantity: int
    price_per_unit: int
    total_price: int
    profit: int | None = None


class MarketScanner:
    def __init__(self, systems_api: SystemsApi):
        self._systems = systems_api

    def get_market_prices(
        self,
        system_symbol: str,
        waypoint_symbol: str,
    ) -> list[MarketPrice]:
        try:
            result = self._systems.get_market(
                system_symbol=system_symbol,
                waypoint_symbol=waypoint_symbol,
            )
            if not result.data:
                return []

            prices = []
            for trade_good in result.data.trade_goods:
                supply = SupplyLevel.MODERATE
                if trade_good.supply:
                    try:
                        supply = SupplyLevel(trade_good.supply.value)
                    except ValueError:
                        pass

                prices.append(
                    MarketPrice(
                        good=trade_good.symbol,
                        symbol=waypoint_symbol,
                        purchase_price=trade_good.purchase_price or 0,
                        sell_price=trade_good.sell_price or 0,
                        supply=supply,
                        trade_volume=trade_good.trade_volume or 0,
                    ),
                )
            return prices
        except Exception:
            return []


class TradingBot:
    def __init__(
        self,
        fleet_api: FleetApi,
        systems_api: SystemsApi,
        fleet_manager: FleetManager,
        min_profit_per_unit: int = 100,
    ):
        self._fleet = fleet_api
        self._systems = systems_api
        self._fleet_manager = fleet_manager
        self._scanner = MarketScanner(systems_api)
        self._min_profit_per_unit = min_profit_per_unit
        self._trade_history: list[TradeResult] = []

    def find_arbitrage(
        self,
        markets: dict[str, list[MarketPrice]],
    ) -> list[TradeOpportunity]:
        opportunities = []
        market_symbols = list(markets.keys())

        for i, buy_market in enumerate(market_symbols):
            for sell_market in market_symbols[i + 1 :]:
                buy_prices = {p.good: p for p in markets[buy_market]}
                sell_prices = {p.good: p for p in markets[sell_market]}

                for good, buy_data in buy_prices.items():
                    if good not in sell_prices:
                        continue

                    sell_data = sell_prices[good]
                    profit = sell_data.sell_price - buy_data.purchase_price

                    if profit >= self._min_profit_per_unit:
                        max_units = min(
                            buy_data.trade_volume,
                            sell_data.trade_volume,
                        )
                        if max_units > 0:
                            opportunities.append(
                                TradeOpportunity(
                                    buy_market=buy_market,
                                    sell_market=sell_market,
                                    good=good,
                                    buy_price=buy_data.purchase_price,
                                    sell_price=sell_data.sell_price,
                                    profit_per_unit=profit,
                                    max_units=max_units,
                                    expected_profit=profit * max_units,
                                ),
                            )

        return sorted(opportunities, key=lambda x: -x.expected_profit)

    async def execute_trade(
        self,
        ship: TrackedShip,
        opportunity: TradeOpportunity,
        quantity: int,
    ) -> TradeResult:
        ship.is_busy = True
        ship.last_action = f"trading {opportunity.good}"

        try:
            await self._fleet._api_client.call_api(
                "/my/ships/{ship_symbol}/purchase",
                "POST",
                path_params={"ship_symbol": ship.symbol},
                body={"trade_symbol": opportunity.good, "units": quantity},
            )

            result = TradeResult(
                timestamp=datetime.now(),
                ship_symbol=ship.symbol,
                action=TradeAction.BUY,
                good=opportunity.good,
                quantity=quantity,
                price_per_unit=opportunity.buy_price,
                total_price=opportunity.buy_price * quantity,
            )

            ship.is_busy = False
            return result

        except Exception as e:
            ship.is_busy = False
            raise e

    def get_trade_history(
        self,
        ship_symbol: str | None = None,
        limit: int = 100,
    ) -> list[TradeResult]:
        history = self._trade_history
        if ship_symbol:
            history = [t for t in history if t.ship_symbol == ship_symbol]
        return history[-limit:]

    def get_total_profit(self, ship_symbol: str | None = None) -> int:
        history = self.get_trade_history(ship_symbol)
        return sum(t.profit or 0 for t in history)


class CargoManager:
    def __init__(self, fleet_api: FleetApi):
        self._fleet = fleet_api
        self._transfers: list[dict] = []

    async def transfer_cargo(
        self,
        from_ship: TrackedShip,
        to_ship: TrackedShip,
        good: str,
        quantity: int,
    ) -> dict:
        from_ship.is_busy = True
        to_ship.is_busy = True

        try:
            result = self._fleet.transfer_cargo(
                ship_symbol=from_ship.symbol,
                transfer_cargo_request={
                    "ship_symbol": to_ship.symbol,
                    "trade_symbol": good,
                    "units": quantity,
                },
            )

            transfer_record = {
                "from": from_ship.symbol,
                "to": to_ship.symbol,
                "good": good,
                "quantity": quantity,
                "timestamp": datetime.now().isoformat(),
            }
            self._transfers.append(transfer_record)
            return transfer_record

        finally:
            from_ship.is_busy = False
            to_ship.is_busy = False

    def get_transfer_history(self) -> list[dict]:
        return self._transfers
