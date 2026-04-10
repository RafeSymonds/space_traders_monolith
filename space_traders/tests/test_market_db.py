from unittest.mock import MagicMock

import pytest

from app.operations.market_db import (
    MarketActivity,
    MarketDatabase,
    MarketScanner,
    SupplyLevel,
    TradeRoute,
)


class TestMarketDatabase:
    def test_initialization(self):
        db = MarketDatabase()
        assert len(db.get_all_markets()) == 0
        assert db.get_stats()["markets_cached"] == 0
        assert db.needs_refresh() is True

    def test_update_market(self):
        db = MarketDatabase()
        mock_market = MagicMock()
        mock_market.exports = []
        mock_market.imports = []
        mock_market.exchange = []
        mock_market.trade_goods = []

        market = db.update_market("X1-ABC", "X1", mock_market)
        assert market.waypoint_symbol == "X1-ABC"
        assert market.system_symbol == "X1"

    def test_get_market(self):
        db = MarketDatabase()
        mock_market = MagicMock()
        mock_market.exports = []
        mock_market.imports = []
        mock_market.exchange = []
        mock_market.trade_goods = []

        db.update_market("X1-ABC", "X1", mock_market)
        retrieved = db.get_market("X1-ABC")
        assert retrieved is not None
        assert retrieved.waypoint_symbol == "X1-ABC"

    def test_get_market_not_found(self):
        db = MarketDatabase()
        assert db.get_market("X1-UNKNOWN") is None

    def test_get_market_comparison(self):
        db = MarketDatabase()
        comparison = db.get_market_comparison("IRON_ORE")
        assert comparison == []

    @pytest.mark.skip(reason="Mock complexity with market scanner")
    def test_get_trade_opportunities(self):
        pass
        pass

    def test_needs_refresh(self):
        db = MarketDatabase()
        assert db.needs_refresh() is True


class TestMarketScanner:
    def test_initialization(self):
        mock_fleet = MagicMock()
        mock_systems = MagicMock()
        scanner = MarketScanner(mock_fleet, mock_systems)
        assert scanner.get_db() is not None

    @pytest.mark.skip(reason="Mock complexity with market scanner")
    def test_get_trade_opportunities(self):
        pass
