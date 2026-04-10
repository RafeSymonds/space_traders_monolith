from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

from space_traders_api import AgentsApi, Configuration
from space_traders_api.models.get_my_agent200_response import GetMyAgent200Response

router = APIRouter(prefix="/agents", tags=["agents"])

config = Configuration()
api_client = AgentsApi()


@router.get("/me", response_model=GetMyAgent200Response)
def get_my_agent(
    authorization: Annotated[str, Header(description="Bearer token")],
) -> GetMyAgent200Response:
    config.api_key["AgentToken"] = authorization.replace("Bearer ", "")
    api_client = AgentsApi(api_client=config.api_client)
    try:
        return api_client.get_my_agent()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
