from unittest.mock import MagicMock

import pytest

from app.core.fleet_manager import FleetManager
from app.operations.trading import (
    CargoManager,
    MarketPrice,
    MarketScanner,
    SupplyLevel,
    TradeOpportunity,
    TradingBot,
)


@pytest.fixture
def mock_fleet_api():
    return MagicMock()


@pytest.fixture
def mock_systems_api():
    return MagicMock()


@pytest.fixture
def mock_fleet_manager():
    FleetManager._instance = None
    return FleetManager.get_instance()


@pytest.fixture
def trading_bot(mock_fleet_api, mock_systems_api, mock_fleet_manager):
    return TradingBot(
        fleet_api=mock_fleet_api,
        systems_api=mock_systems_api,
        fleet_manager=mock_fleet_manager,
        min_profit_per_unit=100,
    )


class TestMarketScanner:
    def test_get_market_prices_empty(self, mock_systems_api):
        scanner = MarketScanner(mock_systems_api)
        mock_systems_api.get_market.return_value = MagicMock(data=None)

        prices = scanner.get_market_prices("X1-TEST", "X1-TEST-WP1")
        assert prices == []

    def test_get_market_prices_with_data(self, mock_systems_api):
        scanner = MarketScanner(mock_systems_api)

        mock_trade_good = MagicMock()
        mock_trade_good.symbol = "IRON_ORE"
        mock_trade_good.purchase_price = 100
        mock_trade_good.sell_price = 90
        mock_trade_good.supply = MagicMock(value="MODERATE")
        mock_trade_good.trade_volume = 50

        mock_market = MagicMock()
        mock_market.trade_goods = [mock_trade_good]

        mock_systems_api.get_market.return_value = MagicMock(data=mock_market)

        prices = scanner.get_market_prices("X1-TEST", "X1-TEST-WP1")

        assert len(prices) == 1
        assert prices[0].good == "IRON_ORE"
        assert prices[0].purchase_price == 100
        assert prices[0].sell_price == 90
        assert prices[0].supply == SupplyLevel.MODERATE


class TestTradingBot:
    def test_find_arbitrage_no_opportunities(self, trading_bot):
        markets = {
            "X1-TEST-WP1": [
                MarketPrice("IRON", "X1-TEST-WP1", 100, 90, SupplyLevel.MODERATE, 50),
            ],
            "X1-TEST-WP2": [
                MarketPrice("IRON", "X1-TEST-WP2", 100, 90, SupplyLevel.MODERATE, 50),
            ],
        }

        opportunities = trading_bot.find_arbitrage(markets)
        assert len(opportunities) == 0

    def test_find_arbitrage_with_profit(self, trading_bot):
        markets = {
            "X1-TEST-WP1": [
                MarketPrice("IRON_ORE", "X1-TEST-WP1", 50, 45, SupplyLevel.ABUNDANT, 100),
            ],
            "X1-TEST-WP2": [
                MarketPrice("IRON_ORE", "X1-TEST-WP2", 50, 200, SupplyLevel.SCARCE, 50),
            ],
        }

        opportunities = trading_bot.find_arbitrage(markets)

        assert len(opportunities) == 1
        assert opportunities[0].buy_market == "X1-TEST-WP1"
        assert opportunities[0].sell_market == "X1-TEST-WP2"
        assert opportunities[0].profit_per_unit == 150
        assert opportunities[0].max_units == 50
        assert opportunities[0].expected_profit == 7500

    def test_find_arbitrage_below_min_profit(self, trading_bot):
        markets = {
            "X1-TEST-WP1": [
                MarketPrice("IRON_ORE", "X1-TEST-WP1", 100, 95, SupplyLevel.ABUNDANT, 100),
            ],
            "X1-TEST-WP2": [
                MarketPrice("IRON_ORE", "X1-TEST-WP2", 100, 150, SupplyLevel.SCARCE, 50),
            ],
        }

        opportunities = trading_bot.find_arbitrage(markets)
        assert len(opportunities) == 0

    def test_find_arbitrage_sorted_by_profit(self, trading_bot):
        markets = {
            "X1-TEST-WP1": [
                MarketPrice("IRON_ORE", "X1-TEST-WP1", 100, 50, SupplyLevel.ABUNDANT, 100),
                MarketPrice("GOLD_ORE", "X1-TEST-WP1", 100, 200, SupplyLevel.ABUNDANT, 100),
            ],
            "X1-TEST-WP2": [
                MarketPrice("IRON_ORE", "X1-TEST-WP2", 100, 200, SupplyLevel.SCARCE, 100),
                MarketPrice("GOLD_ORE", "X1-TEST-WP2", 100, 300, SupplyLevel.SCARCE, 100),
            ],
        }

        opportunities = trading_bot.find_arbitrage(markets)

        assert len(opportunities) == 2
        assert opportunities[0].good == "GOLD_ORE"
        assert opportunities[0].expected_profit == 20000
        assert opportunities[1].good == "IRON_ORE"
        assert opportunities[1].expected_profit == 10000


class TestTradeOpportunity:
    def test_margin_calculation(self):
        opportunity = TradeOpportunity(
            buy_market="WP1",
            sell_market="WP2",
            good="IRON_ORE",
            buy_price=100,
            sell_price=200,
            profit_per_unit=100,
            max_units=50,
            expected_profit=5000,
        )

        assert opportunity.margin == 1.0

    def test_margin_zero_buy_price(self):
        opportunity = TradeOpportunity(
            buy_market="WP1",
            sell_market="WP2",
            good="IRON_ORE",
            buy_price=0,
            sell_price=200,
            profit_per_unit=200,
            max_units=50,
            expected_profit=10000,
        )

        assert opportunity.margin == 0.0


class TestCargoManager:
    def test_initialization(self, mock_fleet_api):
        manager = CargoManager(mock_fleet_api)
        assert manager._transfers == []

    def test_transfer_history(self, mock_fleet_api):
        manager = CargoManager(mock_fleet_api)

        mock_ship1 = MagicMock()
        mock_ship1.symbol = "SHIP-1"
        mock_ship1.is_busy = False

        mock_ship2 = MagicMock()
        mock_ship2.symbol = "SHIP-2"
        mock_ship2.is_busy = False

        manager._transfers = [
            {
                "from": "SHIP-1",
                "to": "SHIP-2",
                "good": "IRON_ORE",
                "quantity": 50,
                "timestamp": "2024-01-01T00:00:00",
            },
        ]

        history = manager.get_transfer_history()
        assert len(history) == 1
        assert history[0]["from"] == "SHIP-1"
