from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.core.fleet_manager import FleetManager, ShipRole
from app.operations.exploration import (
    ChartResult,
    ExplorationBot,
    FleetCoordinator,
    SystemScanResult,
    WaypointScanResult,
)
from space_traders_api.models import Ship, ShipCargo, ShipNav


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
def exploration_bot(mock_fleet_api, mock_systems_api, mock_fleet_manager):
    return ExplorationBot(
        fleet_api=mock_fleet_api,
        systems_api=mock_systems_api,
        fleet_manager=mock_fleet_manager,
    )


@pytest.fixture
def fleet_coordinator(mock_fleet_api, mock_fleet_manager):
    return FleetCoordinator(
        fleet_api=mock_fleet_api,
        fleet_manager=mock_fleet_manager,
    )


@pytest.fixture
def mock_ship():
    ship = MagicMock(spec=Ship)
    ship.symbol = "EXPLORER-1"
    ship.nav = MagicMock(spec=ShipNav)
    ship.nav.waypoint_symbol = "X1-TEST-1"
    ship.nav.system_symbol = "X1-TEST"
    ship.cargo = MagicMock(spec=ShipCargo)
    ship.cargo.capacity = 50
    ship.cargo.units = 0
    return ship


class TestExplorationBot:
    def test_initialization(self, exploration_bot):
        assert exploration_bot._fleet is not None
        assert exploration_bot._systems is not None

    def test_scan_system_success(self, exploration_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.EXPLORATION)

        mock_waypoint1 = MagicMock()
        mock_waypoint1.symbol = "X1-TEST-WP1"
        mock_waypoint2 = MagicMock()
        mock_waypoint2.symbol = "X1-TEST-WP2"

        mock_faction = MagicMock()
        mock_faction.symbol = "COSMIC"

        mock_scan = MagicMock()
        mock_scan.waypoints = [mock_waypoint1, mock_waypoint2]
        mock_scan.factions = [mock_faction]

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.scan = mock_scan

        exploration_bot._fleet.create_ship_system_scan.return_value = mock_response

        result = exploration_bot.scan_system(tracked, "X1-TEST")

        assert result.ship_symbol == "EXPLORER-1"
        assert result.system == "X1-TEST"
        assert result.waypoints_found == 2
        assert result.factions_found == 1
        assert tracked.is_busy is False

    def test_scan_waypoints_success(self, exploration_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.EXPLORATION)

        mock_trait = MagicMock()
        mock_trait.symbol = MagicMock(value="MARKETPLACE")

        mock_modifier = MagicMock()
        mock_modifier.symbol = MagicMock(value="STRIPPED")

        mock_wp = MagicMock()
        mock_wp.symbol = "X1-TEST-WP1"
        mock_wp.traits = [mock_trait]
        mock_wp.modifiers = [mock_modifier]

        mock_scan = MagicMock()
        mock_scan.waypoints = [mock_wp]

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.scan = mock_scan

        exploration_bot._fleet.create_ship_waypoint_scan.return_value = mock_response

        results = exploration_bot.scan_waypoints(tracked)

        assert len(results) == 1
        assert results[0].waypoint == "X1-TEST-WP1"
        assert tracked.is_busy is False

    def test_chart_waypoint_success(self, exploration_bot, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.EXPLORATION)

        mock_chart = MagicMock()
        mock_chart.submitted_by = "AGENT-1"

        mock_response = MagicMock()
        mock_response.data = MagicMock()
        mock_response.data.chart = mock_chart

        exploration_bot._fleet.create_chart.return_value = mock_response

        result = exploration_bot.chart_waypoint(tracked, "X1-TEST-WP1")

        assert result.waypoint == "X1-TEST-WP1"
        assert result.submitted_by == "AGENT-1"
        assert tracked.is_busy is False


class TestFleetCoordinator:
    def test_initialization(self, fleet_coordinator):
        assert fleet_coordinator._missions == []

    def test_assign_role_success(self, fleet_coordinator, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.TRANSPORT)

        result = fleet_coordinator.assign_role("EXPLORER-1", ShipRole.EXPLORATION)

        assert result["success"] is True
        assert result["role"] == "exploration"
        assert tracked.role == ShipRole.EXPLORATION

    def test_assign_role_ship_not_found(self, fleet_coordinator):
        result = fleet_coordinator.assign_role("NONEXISTENT", ShipRole.MINING)

        assert result["success"] is False
        assert "not found" in result["error"]

    def test_get_ships_by_role(self, fleet_coordinator, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        fleet_manager.add_ship(mock_ship, ShipRole.EXPLORATION)

        ships = fleet_coordinator.get_ships_by_role(ShipRole.EXPLORATION)
        assert len(ships) == 1

        ships = fleet_coordinator.get_ships_by_role(ShipRole.MINING)
        assert len(ships) == 0

    def test_get_available_ships(self, fleet_coordinator, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.EXPLORATION)

        available = fleet_coordinator.get_available_ships()
        assert len(available) == 1

        tracked.is_busy = True
        available = fleet_coordinator.get_available_ships()
        assert len(available) == 0

    def test_create_mining_fleet(self, fleet_coordinator, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        fleet_manager.add_ship(mock_ship, ShipRole.TRANSPORT)

        result = fleet_coordinator.create_mining_fleet(num_miners=1)

        assert result["success"] is True
        assert len(result["miners"]) == 1

    def test_create_trading_fleet(self, fleet_coordinator, mock_ship, mock_fleet_manager):
        fleet_manager = mock_fleet_manager
        fleet_manager.add_ship(mock_ship, ShipRole.TRANSPORT)

        result = fleet_coordinator.create_trading_fleet(num_traders=1)

        assert result["success"] is True
        assert len(result["traders"]) == 1


class TestSystemScanResult:
    def test_creation(self):
        result = SystemScanResult(
            ship_symbol="EXPLORER-1",
            system="X1-TEST",
            waypoints_found=10,
            factions_found=3,
            timestamp=datetime.now(),
        )

        assert result.system == "X1-TEST"
        assert result.waypoints_found == 10
        assert result.factions_found == 3


class TestWaypointScanResult:
    def test_creation(self):
        result = WaypointScanResult(
            ship_symbol="EXPLORER-1",
            waypoint="X1-TEST-WP1",
            traits=["MARKETPLACE", "SHIPYARD"],
            modifiers=["STRIPPED"],
            timestamp=datetime.now(),
        )

        assert result.waypoint == "X1-TEST-WP1"
        assert len(result.traits) == 2
        assert len(result.modifiers) == 1


class TestChartResult:
    def test_creation(self):
        result = ChartResult(
            ship_symbol="EXPLORER-1",
            waypoint="X1-TEST-WP1",
            submitted_by="AGENT-1",
            timestamp=datetime.now(),
        )

        assert result.waypoint == "X1-TEST-WP1"
        assert result.submitted_by == "AGENT-1"
