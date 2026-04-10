from unittest.mock import MagicMock

import pytest

from app.core.fleet_manager import FleetManager, ShipRole, TrackedShip
from space_traders_api.models import Ship, ShipCargo, ShipNav


@pytest.fixture
def mock_ship():
    ship = MagicMock(spec=Ship)
    ship.symbol = "SHIP-1"
    ship.nav = MagicMock(spec=ShipNav)
    ship.nav.waypoint_symbol = "X1-TEST-1"
    ship.nav.system_symbol = "X1-TEST"
    ship.nav.status = MagicMock()
    ship.nav.status.value = "DOCKED"
    ship.cargo = MagicMock(spec=ShipCargo)
    ship.cargo.capacity = 100
    ship.cargo.units = 25
    return ship


@pytest.fixture
def fleet_manager():
    FleetManager._instance = None
    return FleetManager.get_instance()


class TestFleetManager:
    def test_singleton_pattern(self, fleet_manager):
        manager1 = FleetManager.get_instance()
        manager2 = FleetManager.get_instance()
        assert manager1 is manager2

    def test_add_ship(self, fleet_manager, mock_ship):
        tracked = fleet_manager.add_ship(mock_ship, ShipRole.MINING)

        assert tracked.symbol == "SHIP-1"
        assert tracked.role == ShipRole.MINING
        assert tracked.current_waypoint == "X1-TEST-1"
        assert tracked.system == "X1-TEST"
        assert tracked.is_busy is False

    def test_get_ship(self, fleet_manager, mock_ship):
        fleet_manager.add_ship(mock_ship, ShipRole.MINING)

        found = fleet_manager.get_ship("SHIP-1")
        assert found is not None
        assert found.symbol == "SHIP-1"

        not_found = fleet_manager.get_ship("NONEXISTENT")
        assert not_found is None

    def test_get_ships_by_role(self, fleet_manager):
        ship1 = MagicMock(spec=Ship)
        ship1.symbol = "MINER-1"
        ship1.nav = MagicMock()
        ship1.nav.waypoint_symbol = None
        ship1.nav.system_symbol = None
        ship1.cargo = MagicMock()
        ship1.cargo.capacity = 0
        ship1.cargo.units = 0

        ship2 = MagicMock(spec=Ship)
        ship2.symbol = "TRADER-1"
        ship2.nav = MagicMock()
        ship2.nav.waypoint_symbol = None
        ship2.nav.system_symbol = None
        ship2.cargo = MagicMock()
        ship2.cargo.capacity = 0
        ship2.cargo.units = 0

        ship3 = MagicMock(spec=Ship)
        ship3.symbol = "MINER-2"
        ship3.nav = MagicMock()
        ship3.nav.waypoint_symbol = None
        ship3.nav.system_symbol = None
        ship3.cargo = MagicMock()
        ship3.cargo.capacity = 0
        ship3.cargo.units = 0

        fleet_manager.add_ship(ship1, ShipRole.MINING)
        fleet_manager.add_ship(ship2, ShipRole.TRADING)
        fleet_manager.add_ship(ship3, ShipRole.MINING)

        miners = fleet_manager.get_ships_by_role(ShipRole.MINING)
        traders = fleet_manager.get_ships_by_role(ShipRole.TRADING)

        assert len(miners) == 2
        assert len(traders) == 1

    def test_get_available_ships(self, fleet_manager):
        ship1 = MagicMock(spec=Ship)
        ship1.symbol = "SHIP-1"
        ship1.nav = MagicMock()
        ship1.nav.waypoint_symbol = None
        ship1.nav.system_symbol = None
        ship1.cargo = MagicMock()
        ship1.cargo.capacity = 0
        ship1.cargo.units = 0

        ship2 = MagicMock(spec=Ship)
        ship2.symbol = "SHIP-2"
        ship2.nav = MagicMock()
        ship2.nav.waypoint_symbol = None
        ship2.nav.system_symbol = None
        ship2.cargo = MagicMock()
        ship2.cargo.capacity = 0
        ship2.cargo.units = 0

        fleet_manager.add_ship(ship1, ShipRole.MINING)
        tracked2 = fleet_manager.add_ship(ship2, ShipRole.TRADING)
        tracked2.is_busy = True

        available = fleet_manager.get_available_ships()
        assert len(available) == 1
        assert available[0].symbol == "SHIP-1"

    def test_refresh_ship(self, fleet_manager, mock_ship):
        fleet_manager.add_ship(mock_ship, ShipRole.TRADING)

        updated_ship = MagicMock(spec=Ship)
        updated_ship.symbol = "SHIP-1"
        updated_ship.nav = MagicMock()
        updated_ship.nav.waypoint_symbol = "X1-TEST-2"
        updated_ship.nav.system_symbol = "X1-TEST"
        updated_ship.cargo = MagicMock()
        updated_ship.cargo.capacity = 100
        updated_ship.cargo.units = 50

        fleet_manager.refresh_ship(updated_ship)

        tracked = fleet_manager.get_ship("SHIP-1")
        assert tracked.current_waypoint == "X1-TEST-2"
        assert tracked.cargo_used == 50


class TestTrackedShip:
    def test_cargo_properties(self, mock_ship):
        tracked = TrackedShip(ship=mock_ship, role=ShipRole.MINING)

        assert tracked.cargo_capacity == 100
        assert tracked.cargo_used == 25
        assert tracked.cargo_available == 75

    def test_symbol_property(self, mock_ship):
        tracked = TrackedShip(ship=mock_ship, role=ShipRole.MINING)
        assert tracked.symbol == "SHIP-1"
