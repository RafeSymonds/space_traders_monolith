
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import Config
from app.core.fleet_manager import FleetManager, ShipRole
from space_traders_api import AgentsApi, ContractsApi, FleetApi, SystemsApi
from space_traders_api.models import NavigateShipRequest

router = APIRouter(prefix="/fleet", tags=["fleet"])


def get_config() -> Config:
    return Config.get_instance()


def get_fleet_api(config: Config = Depends(get_config)):
    return FleetApi(api_client=config.get_api_client())


def get_systems_api(config: Config = Depends(get_config)):
    return SystemsApi(api_client=config.get_api_client())


def get_agents_api(config: Config = Depends(get_config)):
    return AgentsApi(api_client=config.get_api_client())


def get_fleet_manager():
    return FleetManager.get_instance()


class NavigateRequest(BaseModel):
    waypoint: str


class FleetStatusResponse(BaseModel):
    ships: list[dict]
    total: int


@router.get("/", response_model=FleetStatusResponse)
async def get_fleet(
    fleet_api: FleetApi = Depends(get_fleet_api),
    fleet_manager: FleetManager = Depends(get_fleet_manager),
):
    result = fleet_api.get_my_ships()
    ships = []
    for ship_data in result.data:
        tracked = fleet_manager.get_ship(ship_data.symbol)
        if not tracked:
            role = ShipRole.TRANSPORT
            if "MINING" in ship_data.frame.name.upper():
                role = ShipRole.MINING
            elif "EXPLORER" in ship_data.frame.name.upper():
                role = ShipRole.EXPLORATION
            tracked = fleet_manager.add_ship(ship_data, role)

        ships.append(
            {
                "symbol": ship_data.symbol,
                "role": tracked.role.value,
                "system": ship_data.nav.system_symbol if ship_data.nav else None,
                "waypoint": ship_data.nav.waypoint_symbol if ship_data.nav else None,
                "status": ship_data.nav.status.value if ship_data.nav else "unknown",
                "busy": tracked.is_busy,
                "cargo": {
                    "used": ship_data.cargo.units if ship_data.cargo else 0,
                    "capacity": ship_data.cargo.capacity if ship_data.cargo else 0,
                },
            },
        )

    return FleetStatusResponse(ships=ships, total=len(ships))


@router.post("/{ship_symbol}/dock")
async def dock_ship(
    ship_symbol: str,
    fleet_api: FleetApi = Depends(get_fleet_api),
    fleet_manager: FleetManager = Depends(get_fleet_manager),
):
    tracked = fleet_manager.get_ship(ship_symbol)
    if not tracked:
        raise HTTPException(status_code=404, detail="Ship not found")

    result = fleet_api.dock_ship(ship_symbol=ship_symbol)
    return {"success": True, "ship": ship_symbol, "status": "docked"}


@router.post("/{ship_symbol}/orbit")
async def orbit_ship(
    ship_symbol: str,
    fleet_api: FleetApi = Depends(get_fleet_api),
    fleet_manager: FleetManager = Depends(get_fleet_manager),
):
    tracked = fleet_manager.get_ship(ship_symbol)
    if not tracked:
        raise HTTPException(status_code=404, detail="Ship not found")

    result = fleet_api.orbit_ship(ship_symbol=ship_symbol)
    return {"success": True, "ship": ship_symbol, "status": "orbiting"}


@router.post("/{ship_symbol}/navigate")
async def navigate_ship(
    ship_symbol: str,
    request: NavigateRequest,
    fleet_api: FleetApi = Depends(get_fleet_api),
    fleet_manager: FleetManager = Depends(get_fleet_manager),
):
    tracked = fleet_manager.get_ship(ship_symbol)
    if not tracked:
        raise HTTPException(status_code=404, detail="Ship not found")

    nav_request = NavigateShipRequest(waypointSymbol=request.waypoint)
    result = fleet_api.navigate_ship(ship_symbol=ship_symbol, navigate_ship_request=nav_request)
    return {
        "success": True,
        "ship": ship_symbol,
        "destination": request.waypoint,
        "status": result.data.nav.status.value if result.data else "unknown",
    }


@router.post("/{ship_symbol}/extract")
async def extract(
    ship_symbol: str,
    fleet_api: FleetApi = Depends(get_fleet_api),
    fleet_manager: FleetManager = Depends(get_fleet_manager),
):
    tracked = fleet_manager.get_ship(ship_symbol)
    if not tracked:
        raise HTTPException(status_code=404, detail="Ship not found")

    result = fleet_api.extract_resources(ship_symbol=ship_symbol)
    extracts = []
    if result.data and result.data.extraction:
        y = result.data.extraction.var_yield
        extracts.append({"symbol": y.symbol, "units": y.units})

    return {
        "ship": ship_symbol,
        "extracts": extracts,
        "cooldown": result.data.cooldown.remaining_seconds if result.data and result.data.cooldown else 0,
    }


@router.post("/{ship_symbol}/survey")
async def survey(
    ship_symbol: str,
    fleet_api: FleetApi = Depends(get_fleet_api),
    fleet_manager: FleetManager = Depends(get_fleet_manager),
):
    tracked = fleet_manager.get_ship(ship_symbol)
    if not tracked:
        raise HTTPException(status_code=404, detail="Ship not found")

    result = fleet_api.create_survey(ship_symbol=ship_symbol)
    surveys = []
    if result.data and result.data.surveys:
        for s in result.data.surveys:
            surveys.append(
                {
                    "signature": s.signature,
                    "symbol": s.symbol,
                    "expiration": s.expiration.isoformat() if s.expiration else None,
                    "size": s.size.value if s.size else None,
                },
            )

    return {"ship": ship_symbol, "surveys": surveys}


@router.get("/agent")
async def get_agent(
    agents_api: AgentsApi = Depends(get_agents_api),
):
    result = agents_api.get_my_agent()
    return result.data


@router.get("/contracts")
async def get_contracts(
    contracts_api: ContractsApi = Depends(get_agents_api),
):
    result = contracts_api.get_contracts()
    return result.data
