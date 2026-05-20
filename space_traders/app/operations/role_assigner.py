from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable

from app.core.fleet_manager import FleetManager, ShipRole, TrackedShip
from app.operations.market_db import MarketDatabase, SupplyLevel


class MarketCondition(Enum):
    BULL_MARKET = "bull"  # Prices rising, good for selling
    BEAR_MARKET = "bear"  # Prices falling, good for buying
    VOLATILE = "volatile"  # High price swings, opportunity trading
    STABLE = "stable"  # Low movement, hold


@dataclass
class RoleScore:
    role: ShipRole
    score: float
    reasons: list[str]
    urgency: float


@dataclass
class DynamicAssignment:
    ship_symbol: str
    from_role: ShipRole
    to_role: ShipRole
    score: float
    reason: str
    timestamp: datetime


class DynamicRoleAssigner:
    def __init__(
        self,
        fleet_manager: FleetManager,
        market_db: MarketDatabase,
    ):
        self._fleet_manager = fleet_manager
        self._market_db = market_db
        self._assignment_history: list[DynamicAssignment] = []
        self._last_analysis = datetime.min
        self._analysis_cooldown = timedelta(seconds=30)

    def analyze_and_assign(self) -> list[DynamicAssignment]:
        if datetime.now() - self._last_analysis < self._analysis_cooldown:
            return []

        self._last_analysis = datetime.now()
        assignments = []

        mining_score = self._score_mining_role()
        trading_score = self._score_trading_role()

        for ship in self._fleet_manager.ships.values():
            if ship.is_busy:
                continue

            current_score = self._score_ship_for_role(ship, ship.role)

            if mining_score > current_score + 0.2:
                assignments.append(
                    self._create_assignment(ship, ship.role, ShipRole.MINING, mining_score, "Mining profit > trading")
                )
            elif trading_score > current_score + 0.2:
                assignments.append(
                    self._create_assignment(ship, ship.role, ShipRole.TRADING, trading_score, "Trading profit > mining")
                )

        for assignment in assignments:
            self._fleet_manager.get_ship(assignment.ship_symbol).role = assignment.to_role
            self._assignment_history.append(assignment)

        return assignments

    def _score_mining_role(self) -> float:
        mining_locations = self._market_db.find_mining_markets()
        if not mining_locations:
            return 0.3

        avg_price = sum(loc["price"] for loc in mining_locations) / len(mining_locations)
        scarcity_bonus = sum(1 for loc in mining_locations if loc["demand"] == "HIGH") * 0.3

        return min(1.0, 0.4 + (avg_price / 10000) * 0.3 + scarcity_bonus)

    def _score_trading_role(self) -> float:
        opportunities = self._market_db.get_trade_opportunities(min_profit=500, min_volume=5)
        if not opportunities:
            return 0.3

        best_profit = max(opp["total_profit"] for opp in opportunities)
        num_opportunities = len(opportunities)

        return min(1.0, 0.4 + (best_profit / 50000) * 0.3 + num_opportunities * 0.05)

    def _score_ship_for_role(self, ship: TrackedShip, role: ShipRole) -> float:
        if role == ShipRole.MINING:
            return 0.7 if "MINING" in str(ship.ship.frame.name) else 0.4
        elif role == ShipRole.TRADING:
            return 0.7 if any(t in str(ship.ship.frame.name) for t in ["FRIGATE", "HAULER", "FREIGHTER"]) else 0.4
        return 0.5

    def _create_assignment(
        self,
        ship: TrackedShip,
        from_role: ShipRole,
        to_role: ShipRole,
        score: float,
        reason: str,
    ) -> DynamicAssignment:
        return DynamicAssignment(
            ship_symbol=ship.symbol,
            from_role=from_role,
            to_role=to_role,
            score=score,
            reason=reason,
            timestamp=datetime.now(),
        )

    def get_market_condition(self) -> MarketCondition:
        if not self._market_db.get_all_markets():
            return MarketCondition.STABLE

        opportunities = self._market_db.get_trade_opportunities(min_profit=200, min_volume=5)

        if len(opportunities) > 10:
            return MarketCondition.BULL_MARKET
        elif len(opportunities) < 3:
            return MarketCondition.BEAR_MARKET
        elif any(o["efficiency"] > 50 for o in opportunities):
            return MarketCondition.VOLATILE
        return MarketCondition.STABLE

    def get_assignment_stats(self) -> dict:
        return {
            "total_assignments": len(self._assignment_history),
            "market_condition": self.get_market_condition().value,
            "mining_score": self._score_mining_role(),
            "trading_score": self._score_trading_role(),
            "recent_assignments": [
                {
                    "ship": a.ship_symbol,
                    "from": a.from_role.value,
                    "to": a.to_role.value,
                    "reason": a.reason,
                    "timestamp": a.timestamp.isoformat(),
                }
                for a in self._assignment_history[-10:]
            ],
        }


class SmartTaskAssigner:
    def __init__(
        self,
        fleet_manager: FleetManager,
        market_db: MarketDatabase,
    ):
        self._fleet_manager = fleet_manager
        self._market_db = market_db

    def get_best_task(self, ship: TrackedShip) -> dict:
        ship_cargo = ship.cargo_used
        cargo_capacity = ship.cargo_capacity

        if cargo_capacity == 0:
            return {"task": "IDLE", "priority": 0}

        cargo_ratio = ship_cargo / cargo_capacity if cargo_capacity > 0 else 0

        if cargo_ratio < 0.2:
            return self._get_loading_task(ship)
        elif cargo_ratio > 0.8:
            return self._get_selling_task(ship)
        else:
            return self._get_mid_task(ship)

    def _get_loading_task(self, ship: TrackedShip) -> dict:
        mining_locations = self._market_db.find_mining_markets()

        if mining_locations:
            best = mining_locations[0]
            return {
                "task": "MINE",
                "priority": 0.9,
                "target": best["waypoint"],
                "resource": best["resource"],
            }

        return {"task": "FIND_CARGO", "priority": 0.5}

    def _get_selling_task(self, ship: TrackedShip) -> dict:
        opportunities = self._market_db.get_trade_opportunities(min_profit=100, min_volume=1)

        if opportunities:
            best = opportunities[0]
            return {
                "task": "SELL",
                "priority": 0.95,
                "target": best["sell_location"],
                "good": best["trade_good"],
            }

        return {"task": "FIND_BUYER", "priority": 0.5}

    def _get_mid_task(self, ship: TrackedShip) -> dict:
        return {"task": "CONTINUE_MINING", "priority": 0.7}

    def assign_optimal_tasks(self) -> list[dict]:
        assignments = []
        for ship in self._fleet_manager.ships.values():
            if ship.is_busy:
                continue

            task = self.get_best_task(ship)
            assignments.append(
                {
                    "ship": ship.symbol,
                    "current_role": ship.role.value,
                    "suggested_task": task,
                }
            )

        return assignments
