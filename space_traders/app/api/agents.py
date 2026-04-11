from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header

from app.core.config import Config
from space_traders_api import AgentsApi

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agents_api(config: Config = Depends(Config.get_instance)):
    return AgentsApi(api_client=config.get_api_client())


@router.get("/me")
async def get_my_agent(
    authorization: Annotated[str, Header(description="Bearer token")],
    agents_api: AgentsApi = Depends(get_agents_api),
):
    try:
        return agents_api.get_my_agent()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
