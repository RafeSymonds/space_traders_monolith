from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from app.operations.market_db import MarketDatabase, WaypointMarket, MarketTradeGood, SupplyLevel, TradeRoute


class EconomicPhase(Enum):
    EXPANSION = "expansion"  # Accumulating wealth
    CONTRACTION = "contraction"  # Preserving capital
    Peak = "peak"  # Selling high
    Trough = "trough"  # Buying low


class TradeStrategy(Enum):
    SCALPING = "scalping"  # Quick small profits
    SWING = "swing"  # Hold for larger moves
    ARBITRAGE = "arbitrage"  # Exploit market inefficiencies
    SPECULATIVE = "speculative"  # Anticipate future moves


@dataclass
class PricePoint:
    price: int
    timestamp: datetime
    supply: SupplyLevel


@dataclass
class PriceTrend:
    good_symbol: str
    waypoint: str
    direction: float
    velocity: float
    confidence: float
    predicted_next: int


@dataclass
class EconomicOpportunity:
    type: str
    score: float
    route: Optional[TradeRoute] = None
    contract_id: Optional[str] = None
    description: str = ""
    expected_return: float = 0.0
    risk_factor: float = 1.0
    time_horizon_minutes: int = 0
    capital_required: int = 0


@dataclass
class RefineryChain:
    input_good: str
    output_good: str
    refineries: list[str]
    profit_per_unit: int
    time_cost: int


class CargoOptimization:
    @staticmethod
    def optimize_cargo(
        available_goods: list[str],
        ship_capacity: int,
        profit_routes: list[TradeRoute],
    ) -> list[dict]:
        if not profit_routes or ship_capacity == 0:
            return []

        cargo_plan = []
        remaining_capacity = ship_capacity

        sorted_routes = sorted(profit_routes, key=lambda x: x.profit_per_unit * x.route_efficiency, reverse=True)

        for route in sorted_routes:
            if remaining_capacity <= 0:
                break

            units_to_buy = min(route.max_volume, remaining_capacity)
            if units_to_buy > 0:
                cargo_plan.append(
                    {
                        "good": route.trade_good,
                        "buy_from": route.buy_waypoint,
                        "sell_to": route.sell_waypoint,
                        "units": units_to_buy,
                        "expected_profit": route.profit_per_unit * units_to_buy,
                    }
                )
                remaining_capacity -= units_to_buy

        return cargo_plan

    @staticmethod
    def calculate_optimal_split(
        available_routes: list[TradeRoute],
        total_capacity: int,
    ) -> dict[str, int]:
        if not available_routes:
            return {}

        allocations = {}
        remaining = total_capacity

        sorted_routes = sorted(
            available_routes, key=lambda x: x.profit_per_unit / x.buy_price if x.buy_price > 0 else 0, reverse=True
        )

        for route in sorted_routes:
            if remaining <= 0:
                break

            optimal_units = min(route.max_volume, remaining)
            allocations[route.trade_good] = allocations.get(route.trade_good, 0) + optimal_units
            remaining -= optimal_units

        return allocations


class RefineryCoordinator:
    REFINERY_CHAINS = {
        ("IRON_ORE", "IRON"): {"refined_units": 1, "consumed_units": 10, "time_minutes": 5},
        ("COPPER_ORE", "COPPER"): {"refined_units": 1, "consumed_units": 10, "time_minutes": 5},
        ("ALUMINUM_ORE", "ALUMINUM"): {"refined_units": 1, "consumed_units": 10, "time_minutes": 5},
        ("SILICON_ORE", "SILICON"): {"refined_units": 1, "consumed_units": 10, "time_minutes": 5},
        ("GOLD_ORE", "GOLD"): {"refined_units": 1, "consumed_units": 10, "time_minutes": 5},
    }

    def __init__(self, market_db: MarketDatabase):
        self._market_db = market_db
        self._chains: list[RefineryChain] = []
        self._update_chains()

    def _update_chains(self) -> None:
        self._chains = []
        for (input_good, output_good), recipe in self.REFINERY_CHAINS.items():
            input_markets = self._find_markets_selling(input_good)
            output_markets = self._find_markets_buying(output_good)

            for input_market in input_markets:
                for output_market in output_markets:
                    if input_market != output_market:
                        input_price = self._market_db.get_good_price(input_market, input_good)
                        output_price = self._market_db.get_good_price(output_market, output_good)

                        if input_price and output_price:
                            buy_price, _ = input_price
                            _, sell_price = output_price
                            profit = sell_price - (buy_price * recipe["consumed_units"])
                            if profit > 0:
                                self._chains.append(
                                    RefineryChain(
                                        input_good=input_good,
                                        output_good=output_good,
                                        refineries=[output_market],
                                        profit_per_unit=profit,
                                        time_cost=recipe["time_minutes"],
                                    )
                                )

    def _find_markets_selling(self, good: str) -> list[str]:
        markets = []
        for market in self._market_db.get_all_markets():
            for g in market.goods:
                if g.symbol == good and g.purchase_price > 0:
                    markets.append(market.waypoint_symbol)
        return markets

    def _find_markets_buying(self, good: str) -> list[str]:
        markets = []
        for market in self._market_db.get_all_markets():
            for g in market.goods:
                if g.symbol == good and g.sell_price > 0:
                    markets.append(market.waypoint_symbol)
        return markets

    def get_profitable_chains(self, min_profit: int = 100) -> list[RefineryChain]:
        if not self._chains:
            self._update_chains()
        return [c for c in self._chains if c.profit_per_unit >= min_profit]

    def get_best_chain_for_capacity(self, capacity: int) -> RefineryChain | None:
        profitable = self.get_profitable_chains()
        if not profitable:
            return None

        best = None
        best_score = 0

        for chain in profitable:
            chain_capacity = capacity // 10
            total_profit = chain.profit_per_unit * chain_capacity
            score = total_profit / max(chain.time_cost, 1)
            if score > best_score:
                best_score = score
                best = chain

        return best


class PriceAnalyzer:
    def __init__(self, market_db: MarketDatabase):
        self._market_db = market_db

    def get_price_trend(self, good_symbol: str, waypoint: str) -> PriceTrend | None:
        history = self._get_price_history(good_symbol, waypoint, limit=20)
        if len(history) < 3:
            return None

        prices = [p.price for p in history]
        avg_price = sum(prices) / len(prices)

        direction = (prices[-1] - prices[0]) / max(prices[0], 1)
        velocity = direction / len(prices)

        confidence = min(1.0, len(history) / 10)

        predicted = int(prices[-1] * (1 + velocity))

        return PriceTrend(
            good_symbol=good_symbol,
            waypoint=waypoint,
            direction=direction,
            velocity=velocity,
            confidence=confidence,
            predicted_next=predicted,
        )

    def _get_price_history(self, good_symbol: str, waypoint: str, limit: int = 10) -> list[PricePoint]:
        history = [p for p in self._market_db._price_history if p.symbol == good_symbol and p.waypoint == waypoint]
        return history[-limit:]

    def detect_price_anomaly(self, good_symbol: str, waypoint: str) -> bool:
        trend = self.get_price_trend(good_symbol, waypoint)
        if not trend:
            return False

        return abs(trend.direction) > 0.2 or trend.velocity > 0.1

    def predict_price_movement(self, good_symbol: str, waypoint: str, horizon_minutes: int = 30) -> int | None:
        trend = self.get_price_trend(good_symbol, waypoint)
        if not trend or trend.confidence < 0.5:
            return None

        moves_per_minute = trend.velocity
        predicted_change = int(trend.predicted_next * moves_per_minute * horizon_minutes)

        return trend.predicted_next + predicted_change


class EconomicEngine:
    def __init__(self, market_db: MarketDatabase):
        self._market_db = market_db
        self._cargo_optimizer = CargoOptimization()
        self._refinery_coord = RefineryCoordinator(market_db)
        self._price_analyzer = PriceAnalyzer(market_db)
        self._phase = EconomicPhase.EXPANSION
        self._strategy = TradeStrategy.SWING
        self._last_analysis = datetime.min
        self._analysis_interval = timedelta(seconds=30)

    def analyze_market(self) -> list[EconomicOpportunity]:
        if datetime.now() - self._last_analysis < self._analysis_interval:
            return []

        self._last_analysis = datetime.now()
        opportunities = []

        opportunities.extend(self._find_arbitrage_opportunities())
        opportunities.extend(self._find_speculative_opportunities())
        opportunities.extend(self._find_refinery_opportunities())
        opportunities.extend(self._find_contract_opportunities())
        opportunities.extend(self._find_cargo_arbitrage())

        opportunities.sort(key=lambda x: x.score, reverse=True)
        return opportunities[:20]

    def _find_arbitrage_opportunities(self) -> list[EconomicOpportunity]:
        opportunities = []
        routes = self._market_db.find_trade_routes(min_profit=200)

        for route in routes:
            if route.profit_per_unit > 500 and route.route_efficiency > 20:
                opportunities.append(
                    EconomicOpportunity(
                        type="arbitrage",
                        score=route.route_efficiency * route.profit_per_unit / 1000,
                        route=route,
                        description=f"{route.trade_good} {route.buy_waypoint} → {route.sell_waypoint}",
                        expected_return=route.route_efficiency,
                        risk_factor=0.5,
                        time_horizon_minutes=10,
                        capital_required=route.buy_price * route.max_volume,
                    )
                )

        return opportunities

    def _find_speculative_opportunities(self) -> list[EconomicOpportunity]:
        opportunities = []

        for market in self._market_db.get_all_markets():
            for good in market.goods:
                trend = self._price_analyzer.get_price_trend(good.symbol, market.waypoint_symbol)
                if trend and trend.confidence > 0.6:
                    if trend.direction > 0.1:
                        opportunities.append(
                            EconomicOpportunity(
                                type="speculative_buy",
                                score=trend.confidence * trend.direction * 100,
                                description=f"Buy {good.symbol} at {market.waypoint_symbol} - price rising",
                                expected_return=trend.direction * 100,
                                risk_factor=1.5,
                                time_horizon_minutes=30,
                            )
                        )
                    elif trend.direction < -0.1:
                        opportunities.append(
                            EconomicOpportunity(
                                type="speculative_sell",
                                score=abs(trend.confidence * trend.direction * 100),
                                description=f"Sell {good.symbol} at {market.waypoint_symbol} - price falling",
                                expected_return=abs(trend.direction * 100),
                                risk_factor=1.5,
                                time_horizon_minutes=30,
                            )
                        )

        return opportunities

    def _find_refinery_opportunities(self) -> list[EconomicOpportunity]:
        opportunities = []
        chains = self._refinery_coord.get_profitable_chains(min_profit=50)

        for chain in chains:
            opportunities.append(
                EconomicOpportunity(
                    type="refinery",
                    score=chain.profit_per_unit / max(chain.time_cost, 1) * 10,
                    description=f"Refine {chain.input_good} → {chain.output_good} at {chain.refineries[0] if chain.refineries else 'unknown'}",
                    expected_return=chain.profit_per_unit * 10,
                    risk_factor=0.8,
                    time_horizon_minutes=chain.time_cost,
                )
            )

        return opportunities

    def _find_contract_opportunities(self) -> list[EconomicOpportunity]:
        return []

    def _find_cargo_arbitrage(self) -> list[EconomicOpportunity]:
        opportunities = []

        all_routes = self._market_db.get_routes()
        if not all_routes:
            all_routes = self._market_db.find_trade_routes(min_profit=100)

        for route in all_routes[:5]:
            cargo_plan = self._cargo_optimizer.optimize_cargo(
                [route.trade_good],
                100,
                [route],
            )

            if cargo_plan:
                plan = cargo_plan[0]
                opportunities.append(
                    EconomicOpportunity(
                        type="cargo_optimized",
                        score=plan["expected_profit"] / 100,
                        route=route,
                        description=f"Optimal cargo: {plan['units']}x {route.trade_good} for {plan['expected_profit']} profit",
                        expected_return=plan["expected_profit"],
                        risk_factor=0.7,
                        time_horizon_minutes=15,
                    )
                )

        return opportunities

    def get_economic_phase(self) -> EconomicPhase:
        opportunities = self.analyze_market()
        high_urgency = [o for o in opportunities if o.time_horizon_minutes < 10]

        if len(high_urgency) > 5:
            return EconomicPhase.EXPANSION
        elif len(opportunities) < 2:
            return EconomicPhase.CONTRACTION
        elif any(o.type == "speculative_sell" for o in opportunities):
            return EconomicPhase.Peak
        else:
            return EconomicPhase.Trough

    def get_recommended_strategy(self) -> TradeStrategy:
        phase = self.get_economic_phase()

        if phase == EconomicPhase.EXPANSION:
            return TradeStrategy.SCALPING
        elif phase == EconomicPhase.CONTRACTION:
            return TradeStrategy.ARBITRAGE
        elif phase == EconomicPhase.Peak:
            return TradeStrategy.SPECULATIVE
        else:
            return TradeStrategy.SWING

    def get_market_summary(self) -> dict:
        opportunities = self.analyze_market()
        phase = self.get_economic_phase()
        strategy = self.get_recommended_strategy()

        return {
            "phase": phase.value,
            "strategy": strategy.value,
            "opportunities_count": len(opportunities),
            "high_priority": sum(1 for o in opportunities if o.time_horizon_minutes < 10),
            "total_expected_profit": sum(o.expected_return for o in opportunities),
            "best_opportunity": opportunities[0].description if opportunities else None,
            "refinery_chains": len(self._refinery_coord.get_profitable_chains()),
        }


class ContractScorer:
    def __init__(self, market_db: MarketDatabase):
        self._market_db = market_db

    def score_contract(self, contract: dict) -> dict:
        payment_accepted = contract.get("payment", {}).get("onAccepted", 0)
        payment_fulfilled = contract.get("payment", {}).get("onFulfilled", 0)
        total_payment = payment_accepted + payment_fulfilled

        deadline_str = contract.get("deadline", "")
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str.replace("Z", "+00:00"))
                time_remaining = (deadline - datetime.now()).total_seconds() / 3600
            except Exception:
                time_remaining = 168
        else:
            time_remaining = 168

        deliveries = contract.get("terms", {}).get("deliver", [])
        total_units = sum(d.get("unitsRequired", 0) for d in deliveries)

        market_data = self._get_delivery_market_data(deliveries)
        market_efficiency = self._calculate_market_efficiency(deliveries)

        score = (total_payment / max(time_remaining, 1)) * market_efficiency

        return {
            "contract_id": contract.get("id"),
            "score": score,
            "total_payment": total_payment,
            "time_remaining_hours": time_remaining,
            "total_units": total_units,
            "payment_per_unit": total_payment / max(total_units, 1),
            "market_efficiency": market_efficiency,
            "recommended": score > 100,
        }

    def _get_delivery_market_data(self, deliveries: list[dict]) -> dict:
        market_info = {}
        for d in deliveries:
            trade_symbol = d.get("tradeSymbol", "")
            waypoint = d.get("destinationSymbol", "")
            if waypoint:
                market = self._market_db.get_market(waypoint)
                if market:
                    for good in market.goods:
                        if good.symbol == trade_symbol:
                            market_info[trade_symbol] = {
                                "buy_price": good.purchase_price,
                                "sell_price": good.sell_price,
                                "supply": good.supply.value if hasattr(good.supply, "value") else str(good.supply),
                            }
        return market_info

    def _calculate_market_efficiency(self, deliveries: list[dict]) -> float:
        base_efficiency = 1.0

        for d in deliveries:
            trade_symbol = d.get("tradeSymbol", "")
            units_required = d.get("unitsRequired", 0)

            market_data = self._get_delivery_market_data([d])
            if trade_symbol in market_data:
                supply = market_data[trade_symbol].get("supply", "MODERATE")
                if supply in ["SCARCE", "LIMITED"]:
                    base_efficiency *= 1.2
                elif supply == "ABUNDANT":
                    base_efficiency *= 0.8

        return base_efficiency

    def prioritize_contracts(self, contracts: list[dict]) -> list[dict]:
        scored = [self.score_contract(c) for c in contracts]
        return sorted(scored, key=lambda x: x["score"], reverse=True)
