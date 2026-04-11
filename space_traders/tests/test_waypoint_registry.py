import pytest
from datetime import datetime, timedelta

from app.operations.waypoint_registry import WaypointRegistry, WaypointTypeEnum, WaypointTrait, WaypointInfo
from app.operations.ship_navigator import ShipNavigator, ShipNavigationState, ShipActivity


class TestWaypointRegistry:
    def test_singleton(self):
        registry1 = WaypointRegistry.get_instance()
        registry2 = WaypointRegistry.get_instance()
        assert registry1 is registry2

    def test_add_waypoint(self):
        registry = WaypointRegistry()
        mock_waypoint = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-A",
                "type": type("MockType", (), {"value": "PLANET"})(),
                "x": 100,
                "y": -50,
                "traits": [],
                "orbitals": [],
                "faction": None,
            },
        )()

        result = registry.add_waypoint(mock_waypoint, "X1-V16")
        assert result.symbol == "X1-V16-A"
        assert result.system_symbol == "X1-V16"
        assert result.type == "PLANET"

    def test_add_waypoint_with_traits(self):
        registry = WaypointRegistry()
        mock_trait = type(
            "MockTrait",
            (),
            {
                "symbol": type("MockSymbol", (), {"value": "MARKETPLACE"})(),
                "name": "Marketplace",
                "description": "A trading hub",
            },
        )()
        mock_waypoint = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-B",
                "type": type("MockType", (), {"value": "SPACE_STATION"})(),
                "x": 200,
                "y": 100,
                "traits": [mock_trait],
                "orbitals": [],
                "faction": None,
            },
        )()

        result = registry.add_waypoint(mock_waypoint, "X1-V16")
        assert len(result.traits) == 1
        assert result.traits[0].symbol == "MARKETPLACE"
        assert result.is_marketplace

    def test_get_waypoint(self):
        registry = WaypointRegistry()
        mock_waypoint = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-C",
                "type": type("MockType", (), {"value": "ASTEROID_FIELD"})(),
                "x": 0,
                "y": 0,
                "traits": [],
                "orbitals": [],
                "faction": None,
            },
        )()

        registry.add_waypoint(mock_waypoint, "X1-V16")
        result = registry.get_waypoint("X1-V16-C")
        assert result is not None
        assert result.symbol == "X1-V16-C"
        assert result.is_asteroid_field

    def test_get_waypoints_in_system(self):
        registry = WaypointRegistry()
        for symbol in ["X1-V16-A", "X1-V16-B", "X1-DF-55-C"]:
            mock_wp = type(
                "MockWaypoint",
                (),
                {
                    "symbol": symbol,
                    "type": type("MockType", (), {"value": "PLANET"})(),
                    "x": 0,
                    "y": 0,
                    "traits": [],
                    "orbitals": [],
                    "faction": None,
                },
            )()
            registry.add_waypoint(mock_wp, symbol.rsplit("-", 1)[0])

        system_waypoints = registry.get_waypoints_in_system("X1-V16")
        assert len(system_waypoints) == 2

    def test_get_marketplaces(self):
        registry = WaypointRegistry()

        mock_trait = type(
            "MockTrait",
            (),
            {
                "symbol": type("MockSymbol", (), {"value": "MARKETPLACE"})(),
                "name": "Market",
                "description": "",
            },
        )()

        for symbol, is_market in [("X1-V16-A", True), ("X1-V16-B", False), ("X1-V16-C", True)]:
            mock_wp = type(
                "MockWaypoint",
                (),
                {
                    "symbol": symbol,
                    "type": type("MockType", (), {"value": "PLANET"})(),
                    "x": 0,
                    "y": 0,
                    "traits": [mock_trait] if is_market else [],
                    "orbitals": [],
                    "faction": None,
                },
            )()
            registry.add_waypoint(mock_wp, "X1-V16")

        marketplaces = registry.get_marketplaces("X1-V16")
        assert len(marketplaces) == 2

    def test_get_asteroid_fields(self):
        registry = WaypointRegistry()

        for symbol, wp_type in [("X1-V16-A", "ASTEROID_FIELD"), ("X1-V16-B", "PLANET"), ("X1-V16-C", "ASTEROID_FIELD")]:
            mock_wp = type(
                "MockWaypoint",
                (),
                {
                    "symbol": symbol,
                    "type": type("MockType", (), {"value": wp_type})(),
                    "x": 0,
                    "y": 0,
                    "traits": [],
                    "orbitals": [],
                    "faction": None,
                },
            )()
            registry.add_waypoint(mock_wp, "X1-V16")

        asteroids = registry.get_asteroid_fields("X1-V16")
        assert len(asteroids) == 2

    def test_mark_visited(self):
        registry = WaypointRegistry()
        mock_wp = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-X",
                "type": type("MockType", (), {"value": "PLANET"})(),
                "x": 0,
                "y": 0,
                "traits": [],
                "orbitals": [],
                "faction": None,
            },
        )()

        registry.add_waypoint(mock_wp, "X1-V16")
        assert not registry.get_waypoint("X1-V16-X").has_been_visited

        registry.mark_visited("X1-V16-X")
        assert registry.get_waypoint("X1-V16-X").has_been_visited

    def test_market_data_stale(self):
        registry = WaypointRegistry()
        mock_wp = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-Y",
                "type": type("MockType", (), {"value": "PLANET"})(),
                "x": 0,
                "y": 0,
                "traits": [],
                "orbitals": [],
                "faction": None,
            },
        )()

        registry.add_waypoint(mock_wp, "X1-V16")

        assert registry.get_waypoint("X1-V16-Y").market_data_stale

        registry.mark_market_scanned("X1-V16-Y")
        assert not registry.get_waypoint("X1-V16-Y").market_data_stale

    def test_distance_calculation(self):
        registry = WaypointRegistry()

        wp1 = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-1",
                "type": type("MockType", (), {"value": "PLANET"})(),
                "x": 0,
                "y": 0,
                "traits": [],
                "orbitals": [],
                "faction": None,
            },
        )()
        wp2 = type(
            "MockWaypoint",
            (),
            {
                "symbol": "X1-V16-2",
                "type": type("MockType", (), {"value": "PLANET"})(),
                "x": 300,
                "y": 400,
                "traits": [],
                "orbitals": [],
                "faction": None,
            },
        )()

        registry.add_waypoint(wp1, "X1-V16")
        registry.add_waypoint(wp2, "X1-V16")

        distance = registry.distance("X1-V16-1", "X1-V16-2")
        assert abs(distance - 500) < 1


class TestShipNavigator:
    def test_singleton(self):
        nav1 = ShipNavigator.get_instance()
        nav2 = ShipNavigator.get_instance()
        assert nav1 is nav2

    def test_get_state_creates_new(self):
        nav = ShipNavigator()
        state = nav.get_state("SHIP-1")
        assert state.ship_symbol == "SHIP-1"
        assert state.activity == ShipActivity.IDLE

    def test_navigate_ship(self):
        nav = ShipNavigator()
        mock_ship = type("MockShip", (), {"symbol": "SHIP-2", "is_busy": False, "last_action": None})()

        result = nav.navigate_ship(mock_ship, "X1-V16-A", 60)
        assert result["success"]
        assert result["destination"] == "X1-V16-A"

        state = nav.get_state("SHIP-2")
        assert state.is_traveling()
        assert state.destination == "X1-V16-A"

    def test_ship_arrived(self):
        nav = ShipNavigator()
        mock_ship = type("MockShip", (), {"symbol": "SHIP-3", "is_busy": True})()

        nav.navigate_ship(mock_ship, "X1-V16-B", 60)
        nav.ship_arrived("SHIP-3")

        state = nav.get_state("SHIP-3")
        assert not state.is_traveling()
        assert state.destination is None

    def test_set_activity(self):
        nav = ShipNavigator()
        mock_ship = type("MockShip", (), {"symbol": "SHIP-4", "is_busy": False})()

        nav.set_activity("SHIP-4", ShipActivity.MINING, mock_ship)
        state = nav.get_state("SHIP-4")
        assert state.activity == ShipActivity.MINING
        assert mock_ship.is_busy

    def test_get_traveling_ships(self):
        nav = ShipNavigator()
        mock_ship1 = type("MockShip", (), {"symbol": "SHIP-5", "is_busy": False})()
        mock_ship2 = type("MockShip", (), {"symbol": "SHIP-6", "is_busy": False})()

        nav.navigate_ship(mock_ship1, "X1-V16-A", 60)
        nav.set_activity("SHIP-6", ShipActivity.IDLE)

        traveling = nav.get_traveling_ships()
        assert "SHIP-5" in traveling
        assert "SHIP-6" not in traveling


class TestShipNavigationState:
    def test_navigate_to(self):
        state = ShipNavigationState(ship_symbol="TEST-1")
        state.navigate_to("X1-V16-A", 60)

        assert state.activity == ShipActivity.TRAVELING
        assert state.destination == "X1-V16-A"
        assert state.departure_time is not None
        assert state.estimated_arrival is not None

    def test_arrive(self):
        state = ShipNavigationState(ship_symbol="TEST-2")
        state.navigate_to("X1-V16-B", 60)
        state.arrive()

        assert state.destination is None
        assert state.departure_time is None
        assert state.estimated_arrival is None

    def test_should_have_arrived(self):
        state = ShipNavigationState(ship_symbol="TEST-3")
        state.navigate_to("X1-V16-C", 1)
        assert not state.should_have_arrived()

        state.estimated_arrival = datetime.now() - timedelta(seconds=10)
        assert state.should_have_arrived()
