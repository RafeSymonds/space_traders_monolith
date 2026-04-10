from fastapi import APIRouter

from app.api.automation import router as automation_router
from app.api.fleet import router as fleet_router

router = APIRouter()
router.include_router(fleet_router)
router.include_router(automation_router)
