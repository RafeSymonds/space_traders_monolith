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
    logger.info("FULLY AUTOMATIC MODE ENABLED - No manual intervention required")

    async def run_brain_loop():
        while True:
            try:
                status = brain.get_status()
                if status["state"] == "running":
                    result = brain.run_cycle()

                    metrics = status.get("metrics", {})
                    credit_change = metrics.get("total_credits", 0) - getattr(
                        brain, "_last_credits", metrics.get("total_credits", 0)
                    )
                    brain._last_credits = metrics.get("total_credits", 0)

                    logger.info(
                        f"Cycle {result.get('cycle', '?')}: "
                        f"Credits={metrics.get('total_credits', 0):,} "
                        f"(|{credit_change:+}|) "
                        f"Ships={metrics.get('total_ships', 0)} "
                        f"Mining={metrics.get('total_extracted', 0)} "
                        f"Trades={metrics.get('trades_executed', 0)} "
                        f"Condition={metrics.get('market_condition', 'unknown')}"
                    )
                else:
                    logger.warning(f"Brain state is {status['state']}, not running!")
                await asyncio.sleep(15)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Brain cycle error: {e}")
                await asyncio.sleep(15)

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
