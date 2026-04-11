from space_traders_api import AccountsApi, ApiClient, Configuration
from space_traders_api.models import RegisterRequest as STRegisterRequest
from space_traders_api.models.faction_symbol import FactionSymbol

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    agent_symbol: str
    faction: str = "COSMIC"


class RegisterResponse(BaseModel):
    token: str
    agent_symbol: str
    credits: int
    starting_faction: str
    headquarters: str


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    try:
        config = Configuration()
        client = ApiClient(configuration=config)
        accounts_api = AccountsApi(api_client=client)

        register_req = STRegisterRequest(
            symbol=request.agent_symbol,
            faction=FactionSymbol(request.faction),
        )

        result = accounts_api.register(register_request=register_req)

        if result.data and result.data.agent:
            agent = result.data.agent
            return RegisterResponse(
                token=result.data.token,
                agent_symbol=getattr(agent, "symbol", "unknown"),
                credits=getattr(agent, "credits", 0) or 0,
                starting_faction=getattr(agent, "starting_faction", "COSMIC"),
                headquarters=getattr(agent, "headquarters", ""),
            )

        raise HTTPException(status_code=500, detail="Registration failed - no data returned")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
