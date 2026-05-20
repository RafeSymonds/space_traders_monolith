from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from fastapi import APIRouter, Depends

from app.core.config import Config
from app.core.fleet_manager import FleetManager, ShipRole
from app.operations.fleet_brain import FleetBrain
from space_traders_api import ContractsApi, FleetApi

router = APIRouter(prefix="/automation", tags=["automation"])


def get_config() -> Config:
    return Config.get_instance()


def get_fleet_api(config: Config = Depends(get_config)):
    return FleetApi(api_client=config.get_api_client())


def get_contracts_api(config: Config = Depends(get_config)):
    return ContractsApi(api_client=config.get_api_client())


class RoleRequest(BaseModel):
    role: str


class ShipRoleRequest(BaseModel):
    ship_symbol: str
    role: str


class FleetBrainStatusResponse(BaseModel):
    state: str
    auto_mode: bool
    metrics: dict
    last_update: str


class CycleResultResponse(BaseModel):
    success: bool
    results: dict


class ContractDeliveryRequest(BaseModel):
    contract_id: str
    ship_symbol: str
    trade_symbol: str
    units: int


_brain_instance: FleetBrain | None = None


def get_fleet_brain() -> FleetBrain:
    global _brain_instance
    if _brain_instance is None:
        _brain_instance = FleetBrain()
    return _brain_instance


@router.get("/brain/status", response_model=FleetBrainStatusResponse)
async def get_brain_status(brain: FleetBrain = Depends(get_fleet_brain)) -> FleetBrainStatusResponse:
    status = brain.get_status()
    return FleetBrainStatusResponse(
        state=status["state"],
        auto_mode=status["auto_mode"],
        metrics=status["metrics"],
        last_update=status["last_update"],
    )


@router.post("/brain/start")
async def start_brain(brain: FleetBrain = Depends(get_fleet_brain)):
    return brain.start()


@router.post("/brain/pause")
async def pause_brain(brain: FleetBrain = Depends(get_fleet_brain)):
    return brain.pause()


@router.post("/brain/cycle")
async def run_cycle(brain: FleetBrain = Depends(get_fleet_brain)):
    return brain.run_cycle()


@router.post("/fleet/assign-role")
async def assign_role(request: ShipRoleRequest, brain: FleetBrain = Depends(get_fleet_brain)):
    try:
        role = ShipRole(request.role)
    except ValueError:
        return {"success": False, "error": f"Invalid role: {request.role}"}
    return brain.assign_ship_role(request.ship_symbol, role)


@router.post("/fleet/create-mining-fleet")
async def create_mining_fleet(num_ships: int = 3, brain: FleetBrain = Depends(get_fleet_brain)):
    return brain.create_mining_fleet(num_ships)


@router.post("/fleet/create-trading-fleet")
async def create_trading_fleet(num_ships: int = 2, brain: FleetBrain = Depends(get_fleet_brain)):
    return brain.create_trading_fleet(num_ships)


@router.get("/fleet/status")
async def get_fleet_status(brain: FleetBrain = Depends(get_fleet_brain)):
    return {"ships": brain.get_fleet_status()}


@router.get("/contracts/pending")
async def get_pending_contracts(brain: FleetBrain = Depends(get_fleet_brain)):
    return {"contracts": brain.get_pending_contracts()}


@router.get("/trading/opportunities")
async def get_trade_opportunities(min_profit: int = 1000, brain: FleetBrain = Depends(get_fleet_brain)):
    return {"opportunities": brain.get_trade_opportunities(min_profit=min_profit)}


@router.post("/contracts/deliver")
async def deliver_contract(
    request: ContractDeliveryRequest,
    brain: FleetBrain = Depends(get_fleet_brain),
):
    return brain._contract_coord.execute_delivery(
        request.contract_id,
        request.ship_symbol,
        request.trade_symbol,
        request.units,
    )


@router.get("/systems/waypoints")
async def get_system_waypoints(
    system_symbol: str,
    brain: FleetBrain = Depends(get_fleet_brain),
):
    waypoints = brain.get_systems(system_symbol)
    return {"waypoints": waypoints}


@router.get("/expansion/stats")
async def get_expansion_stats(brain: FleetBrain = Depends(get_fleet_brain)):
    return brain._expansion_manager.get_expansion_stats()


@router.get("/trading/multi-hop-routes")
async def get_multi_hop_routes(
    system_symbol: str | None = None,
    min_profit: int = 500,
    max_hops: int = 3,
    brain: FleetBrain = Depends(get_fleet_brain),
):
    if system_symbol:
        routes = brain._route_planner.find_multi_hop_routes(system_symbol, max_hops, min_profit)
        return {
            "routes": [
                {
                    "stops": r.stops,
                    "goods": r.goods,
                    "total_profit": r.total_profit,
                    "estimated_time_minutes": r.estimated_time_minutes,
                    "legs": r.legs,
                }
                for r in routes
            ],
            "count": len(routes),
        }
    return {"routes": [], "count": 0}


@router.get("/trading/role-optimization")
async def get_role_optimization(brain: FleetBrain = Depends(get_fleet_brain)):
    return brain._role_assigner.get_assignment_stats()


@router.post("/trading/execute-route")
async def execute_trade_route(
    buy_waypoint: str,
    sell_waypoint: str,
    trade_good: str,
    ship_symbol: str,
    quantity: int | None = None,
    brain: FleetBrain = Depends(get_fleet_brain),
):
    route = brain._market_scanner.get_db().find_best_route(trade_good, min_profit=100)
    if route:
        execution = brain._trade_executor.execute_trade(route[0], ship_symbol, quantity)
        return {"success": True, "trade": str(execution)}
    return {"success": False, "error": "No route found"}


@router.get("/trading/active-trades")
async def get_active_trades(brain: FleetBrain = Depends(get_fleet_brain)):
    return {
        "trades": [
            {"ship": t.ship_symbol, "state": t.state.value, "route": t.trade_route.trade_good}
            for t in brain._trade_executor._active_trades.values()
        ]
    }


@router.get("/trading/profit-history")
async def get_profit_history(limit: int = 50, brain: FleetBrain = Depends(get_fleet_brain)):
    history = brain._trade_executor.get_trade_history(limit)
    return {
        "total_profit": brain._trade_executor.get_total_profit(),
        "trades": history,
    }


@router.get("/economic/summary")
async def get_economic_summary(brain: FleetBrain = Depends(get_fleet_brain)):
    return brain._economic_engine.get_market_summary()


@router.get("/economic/opportunities")
async def get_economic_opportunities(brain: FleetBrain = Depends(get_fleet_brain)):
    opportunities = brain._economic_engine.analyze_market()
    return {
        "opportunities": [
            {
                "type": o.type,
                "score": o.score,
                "description": o.description,
                "expected_return": o.expected_return,
                "risk_factor": o.risk_factor,
                "time_horizon_minutes": o.time_horizon_minutes,
            }
            for o in opportunities
        ],
        "count": len(opportunities),
    }


@router.get("/contracts/prioritized")
async def get_prioritized_contracts(brain: FleetBrain = Depends(get_fleet_brain)):
    try:
        contracts_result = brain._contracts_api.get_contracts()
        contracts = []
        if contracts_result.data:
            for c in contracts_result.data:
                contracts.append(
                    {
                        "id": c.id,
                        "faction_symbol": c.faction_symbol,
                        "type": c.type,
                        "accepted": c.accepted,
                        "fulfilled": c.fulfilled,
                        "deadline": str(c.deadline) if c.deadline else None,
                        "payment": {
                            "on_accepted": c.payment.on_accepted if c.payment else 0,
                            "on_fulfilled": c.payment.on_fulfilled if c.payment else 0,
                        },
                        "terms": {
                            "deliver": [
                                {
                                    "trade_symbol": d.trade_symbol,
                                    "units_required": d.units_required,
                                    "units_fulfilled": d.units_fulfilled,
                                    "destination_symbol": d.destination_symbol,
                                }
                                for d in (c.terms.deliver or [])
                            ]
                        },
                    }
                )

        scored = brain._contract_scorer.prioritize_contracts(contracts)
        return {"contracts": scored}
    except Exception as e:
        return {"contracts": [], "error": str(e)}
