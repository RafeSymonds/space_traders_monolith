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
