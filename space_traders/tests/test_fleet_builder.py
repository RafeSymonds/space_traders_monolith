from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from app.operations.fleet_builder import (
    FleetExpansionManager,
    ShipPurchaser,
    ShipPurchaseState,
)


class TestShipPurchaser:
    def test_initialization(self):
        mock_fleet = MagicMock()
        purchaser = ShipPurchaser(mock_fleet)

        assert purchaser.get_state() == ShipPurchaseState.IDLE
        assert purchaser.can_purchase(100000) is True
        assert purchaser.can_purchase(30000) is False

    def test_get_available_ships(self):
        mock_fleet = MagicMock()
        mock_result = MagicMock()
        mock_ship1 = MagicMock()
        mock_ship1.type = "SHIP_MINING_DRONE"
        mock_ship1.price = 40000
        mock_ship1.name = "Mining Drone"
        mock_ship1.description = "A small mining vessel"
        mock_ship2 = MagicMock()
        mock_ship2.type = "SHIP_HOOVER"
        mock_ship2.price = 60000
        mock_ship2.name = "Hoover"
        mock_ship2.description = "Gas siphon ship"
        mock_result.data = [mock_ship1, mock_ship2]
        mock_fleet.get_ship_types.return_value = mock_result

        purchaser = ShipPurchaser(mock_fleet, min_credits_before_buy=50000)
        agent = {"credits": 200000}
        ships = purchaser.get_available_ships(agent)

        assert len(ships) == 2
        assert ships[0]["symbol"] == "SHIP_MINING_DRONE"
        assert ships[0]["price"] == 40000
        assert ships[1]["symbol"] == "SHIP_HOOVER"
        assert ships[1]["price"] == 60000

    def test_purchase_ship_success(self):
        mock_fleet = MagicMock()
        mock_ship = MagicMock(symbol="SHIP-123", purchase_price=50000)
        mock_result = MagicMock()
        mock_result.data = MagicMock(agent=MagicMock(), ship=mock_ship)
        mock_fleet.purchase_ship.return_value = mock_result

        purchaser = ShipPurchaser(mock_fleet)
        result = purchaser.purchase_ship("SHIP_MINING_DRONE", "X1-ABC-123")

        assert result.success is True
        assert result.ship_symbol == "SHIP-123"
        assert result.price == 50000

    def test_purchase_ship_failure(self):
        mock_fleet = MagicMock()
        mock_fleet.purchase_ship.side_effect = Exception("Not enough credits")

        purchaser = ShipPurchaser(mock_fleet)
        result = purchaser.purchase_ship("SHIP_MINING_DRONE", "X1-ABC-123")

        assert result.success is False
        assert result.error == "Not enough credits"

    def test_auto_purchase_if_able(self):
        mock_fleet = MagicMock()
        mock_ship = MagicMock(symbol="SHIP-NEW", purchase_price=40000)
        mock_result = MagicMock()
        mock_result.data = MagicMock(agent=MagicMock(), ship=mock_ship)
        mock_fleet.get_ship_types.return_value = MagicMock(
            data=[
                MagicMock(type="SHIP_MINING_DRONE", price=40000, name="Mining Drone"),
            ]
        )
        mock_fleet.purchase_ship.return_value = mock_result

        purchaser = ShipPurchaser(mock_fleet, min_credits_before_buy=50000)
        agent = {"credits": 200000}

        result = purchaser.auto_purchase_if_able(agent, "X1-ABC-123")

        assert result is not None
        assert result.success is True
        assert result.ship_symbol == "SHIP-NEW"

    def test_auto_purchase_insufficient_credits(self):
        mock_fleet = MagicMock()
        purchaser = ShipPurchaser(mock_fleet, min_credits_before_buy=100000)
        agent = {"credits": 50000}

        result = purchaser.auto_purchase_if_able(agent, "X1-ABC-123")

        assert result is None

    def test_get_stats(self):
        mock_fleet = MagicMock()
        purchaser = ShipPurchaser(mock_fleet, min_credits_before_buy=75000)

        stats = purchaser.get_stats()

        assert stats["state"] == "idle"
        assert stats["min_credits_before_buy"] == 75000


class TestFleetExpansionManager:
    def test_initialization(self):
        mock_fleet = MagicMock()
        manager = FleetExpansionManager(mock_fleet)

        assert manager._total_ships_purchased == 0
        assert manager._total_spent == 0

    def test_get_total_ships(self):
        mock_fleet = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [MagicMock(), MagicMock(), MagicMock()]
        mock_fleet.get_my_ships.return_value = mock_result

        manager = FleetExpansionManager(mock_fleet)
        assert manager.get_total_ships() == 3

    def test_get_total_ships_empty(self):
        mock_fleet = MagicMock()
        mock_fleet.get_my_ships.return_value = MagicMock(data=[])

        manager = FleetExpansionManager(mock_fleet)
        assert manager.get_total_ships() == 0

    def test_attempt_expansion_at_target(self):
        mock_fleet = MagicMock()
        mock_result = MagicMock()
        mock_result.data = [MagicMock() for _ in range(10)]
        mock_fleet.get_my_ships.return_value = mock_result

        manager = FleetExpansionManager(mock_fleet)
        result = manager.attempt_expansion({"credits": 1000000}, "X1-ABC-123", target_fleet_size=10)

        assert result is None

    def test_attempt_expansion_purchases(self):
        mock_fleet = MagicMock()
        mock_ships_result = MagicMock()
        mock_ships_result.data = [MagicMock()]
        mock_fleet.get_my_ships.return_value = mock_ships_result

        mock_purchase_result = MagicMock()
        mock_purchase_result.data = MagicMock(
            agent=MagicMock(),
            ship=MagicMock(symbol="SHIP-NEW", purchase_price=50000),
        )
        mock_fleet.purchase_ship.return_value = mock_purchase_result
        mock_fleet.get_ship_types.return_value = MagicMock(
            data=[
                MagicMock(type="SHIP_MINING_DRONE", price=50000, name="Mining Drone"),
            ]
        )

        manager = FleetExpansionManager(mock_fleet)
        result = manager.attempt_expansion({"credits": 200000}, "X1-ABC-123", target_fleet_size=20)

        assert result is not None
        assert result.success is True
        assert manager._total_ships_purchased == 1
        assert manager._total_spent == 50000

    def test_get_expansion_stats(self):
        mock_fleet = MagicMock()
        manager = FleetExpansionManager(mock_fleet)

        stats = manager.get_expansion_stats()

        assert stats["total_ships_purchased"] == 0
        assert stats["total_credits_spent"] == 0
        assert stats["current_purchaser_state"] == "idle"
        assert stats["purchase_history"] == []
