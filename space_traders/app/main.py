import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import router
from app.operations.fleet_brain import FleetBrain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    brain = FleetBrain()
    brain.start()
    logger.info(f"FleetBrain started: state={brain._state.value}, auto_mode={brain._auto_mode}")

    async def run_brain_loop():
        while True:
            try:
                status = brain.get_status()
                if status["state"] == "running":
                    logger.info("Running brain cycle...")
                    result = brain.run_cycle()
                    if result.get("mining", {}).get("total_extracted", 0) > 0:
                        logger.info(f"Mining: extracted {result['mining']['total_extracted']}")
                    if result.get("fuel", {}).get("refueled", 0) > 0:
                        logger.info(f"Fuel: refueled {result['fuel']['refueled']} ships")
                    if result.get("market_discovery", {}).get("discovered", 0) > 0:
                        logger.info(
                            f"Market discovery: found data at {result['market_discovery']['discovered']} markets"
                        )
                else:
                    logger.warning(f"Brain state is {status['state']}, not running!")
                await asyncio.sleep(30)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Brain cycle error: {e}")
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
