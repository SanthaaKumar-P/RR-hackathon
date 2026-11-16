from fastapi import APIRouter
from app.api.routes import (
    overview,
    batters,
    bowlers,
    pressure,
    matches,
    comparison,
    methodology,
    scenarios,
    audit
)

api_router = APIRouter()

api_router.include_router(overview.router)
api_router.include_router(batters.router)
api_router.include_router(bowlers.router)
api_router.include_router(pressure.router)
api_router.include_router(matches.router)
api_router.include_router(comparison.router)
api_router.include_router(methodology.router)
api_router.include_router(scenarios.router)
api_router.include_router(audit.router)

__all__ = ["api_router"]
