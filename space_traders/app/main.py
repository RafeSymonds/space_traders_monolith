import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.operations.fleet_brain import FleetBrain


@asynccontextmanager
async def lifespan(app: FastAPI):
    brain = FleetBrain()
    brain.start()

    async def run_brain_loop():
        while True:
            try:
                if brain.get_status()["state"] == "running":
                    brain.run_cycle()
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception:
                await asyncio.sleep(30)

    task = asyncio.create_task(run_brain_loop())
    app.state.brain_task = task
    app.state.brain = brain

    yield

    task.cancel()


app = FastAPI(
    title="Space Traders API",
    description="FastAPI wrapper for Space Traders game",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")
