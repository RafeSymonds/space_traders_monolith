from datetime import datetime, timedelta
from unittest.mock import MagicMock

import pytest

from app.core.fleet_manager import FleetManager, ShipRole
from app.operations.mining import (
    ExtractionResult,
    GasSiphonBot,
    MiningBot,
    MiningYield,
    RefiningBot,
    SurveyResult,
)
from space_traders_api.models import Ship, ShipCargo, ShipNav


@pytest.fixture
def mock_fleet_api():
    return MagicMock()


@pytest.fixture
def mock_fleet_manager():
    FleetManager._instance = None
    return FleetManager.get_instance()


@pytest.fixture
def mining_bot(mock_fleet_api, mock_fleet_manager):
    return MiningBot(
        fleet_api=mock_fleet_api,
        fleet_manager=mock_fleet_manager,
        cooldown_seconds=60,
    )


@pytest.fixture
def mock_ship():
    ship = MagicMock(spec=Ship)
    ship.symbol = "MINER-1"
    ship.nav = MagicMock(spec=ShipNav)
    ship.nav.waypoint_symbol = "X1-TEST-1"
    ship.nav.system_symbol = "X1-TEST"
    ship.cargo = MagicMock(spec=ShipCargo)
    ship.cargo.capacity = 100
    ship.cargo.units = 0
    return ship


class TestMiningBot:
    def test_initialization(self, mining_bot):
        assert mining_bot._cooldown_seconds == 60
        assert mining_bot._extraction_history == []

    def test_survey_success(self, mining_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.MINING)

        mock_survey = MagicMock()
        mock_survey.symbol = "X1-TEST-1"
        mock_survey.signature = "sig123"
        mock_survey.deposits = [
            MagicMock(symbol="IRON_ORE"),
            MagicMock(symbol="COPPER_ORE"),
        ]
        mock_survey.expiration = datetime.now() + timedelta(hours=1)
        mock_survey.size = MagicMock(value="MODERATE")

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.surveys = [mock_survey]

        mining_bot._fleet.create_survey.return_value = mock_response

        results = mining_bot.survey(tracked)

        assert len(results) == 1
        assert results[0].waypoint == "X1-TEST-1"
        assert "IRON_ORE" in results[0].deposits
        assert results[0].size == "MODERATE"
        assert tracked.is_busy is False

    def test_extract_success(self, mining_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.MINING)

        mock_extraction_yield = MagicMock()
        mock_extraction_yield.symbol = "IRON_ORE"
        mock_extraction_yield.units = 25

        mock_extraction = MagicMock()
        mock_extraction.var_yield = mock_extraction_yield

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.extraction = mock_extraction

        mining_bot._fleet.extract_resources.return_value = mock_response

        result = mining_bot.extract(tracked)

        assert result.ship_symbol == "MINER-1"
        assert len(result.yields) == 1
        assert result.yields[0].good == "IRON_ORE"
        assert result.yields[0].units == 25
        assert result.total_units == 25
        assert tracked.is_busy is False

    def test_extract_updates_history(self, mining_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.MINING)

        mock_extraction_yield = MagicMock()
        mock_extraction_yield.symbol = "IRON_ORE"
        mock_extraction_yield.units = 25

        mock_extraction = MagicMock()
        mock_extraction.var_yield = mock_extraction_yield

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.extraction = mock_extraction

        mining_bot._fleet.extract_resources.return_value = mock_response

        mining_bot.extract(tracked)
        mining_bot.extract(tracked)

        history = mining_bot.get_extraction_history()
        assert len(history) == 2

    def test_get_total_extracted(self, mining_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.MINING)

        goods_and_units = [
            ("IRON_ORE", 25),
            ("COPPER_ORE", 15),
            ("IRON_ORE", 10),
        ]

        for good, units in goods_and_units:
            mock_extraction_yield = MagicMock()
            mock_extraction_yield.symbol = good
            mock_extraction_yield.units = units

            mock_extraction = MagicMock()
            mock_extraction.var_yield = mock_extraction_yield

            mock_response = MagicMock()
            mock_response.data = MagicMock()
            mock_response.data.extraction = mock_extraction

            mining_bot._fleet.extract_resources.return_value = mock_response
            mining_bot.extract(tracked)

        totals = mining_bot.get_total_extracted()
        assert totals["IRON_ORE"] == 35
        assert totals["COPPER_ORE"] == 15


class TestExtractionResult:
    def test_creation(self):
        result = ExtractionResult(
            ship_symbol="MINER-1",
            yields=[MiningYield("IRON_ORE", 25)],
            total_units=25,
            timestamp=datetime.now(),
        )

        assert result.ship_symbol == "MINER-1"
        assert len(result.yields) == 1
        assert result.total_units == 25


class TestSurveyResult:
    def test_creation(self):
        result = SurveyResult(
            ship_symbol="MINER-1",
            waypoint="X1-TEST-1",
            deposits=["IRON_ORE", "COPPER_ORE"],
            expiration=datetime.now() + timedelta(hours=1),
            size="MODERATE",
        )

        assert result.waypoint == "X1-TEST-1"
        assert len(result.deposits) == 2
        assert result.size == "MODERATE"


class TestGasSiphonBot:
    def test_initialization(self, mock_fleet_api, mock_fleet_manager):
        bot = GasSiphonBot(mock_fleet_api, mock_fleet_manager, cooldown_seconds=30)
        assert bot._cooldown_seconds == 30


class TestRefiningBot:
    def test_initialization(self, mock_fleet_api):
        bot = RefiningBot(mock_fleet_api)
        assert bot._fleet == mock_fleet_api
