import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routes import api_router
from app.schemas.common import HealthResponse
from app.services.data_loader import data_loader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("superr_selector.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SupeRR Selector Backend Engine...")
    logger.info(f"Target Project Root: {settings.BASE_DIR.resolve()}")
    try:
        data_loader.load_all_datasets()
        logger.info("All datasets loaded and cached in memory successfully.")
    except Exception as e:
        logger.critical(f"Critical error loading datasets on startup: {str(e)}", exc_info=True)
    yield
    logger.info("Shutting down SupeRR Selector Backend Engine...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred while processing your analytical request.",
            "path": request.url.path
        }
    )

# Root endpoint
@app.get("/", tags=["General"])
def root():
    return {
        "project": "SupeRR Selector – Cricket Intelligence Platform",
        "season": "Season 2",
        "round": "Round 1",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_v1_prefix": settings.API_V1_STR,
        "overview_endpoint": f"{settings.API_V1_STR}/overview"
    }

# Health Check Endpoint
@app.get("/health", response_model=HealthResponse, tags=["General"])
@app.get(f"{settings.API_V1_STR}/health", response_model=HealthResponse, tags=["General"])
def health_check():
    matches = data_loader.get_target_matches()
    pressure = data_loader.get_pressure_classified()
    p_flag = (
        ((pressure["innings"] == 1) & pressure["first_innings_pressure"].isin(["Moderate", "High", "Extreme"])) |
        ((pressure["innings"] == 2) & pressure["chase_pressure"].isin(["Moderate", "High", "Extreme"]))
    )
    return HealthResponse(
        status="ok",
        version=settings.VERSION,
        project="SupeRR Selector – Cricket Intelligence Platform",
        datasets_loaded=True,
        total_matches=len(matches),
        total_pressure_deliveries=int(p_flag.sum())
    )

# Mount all /api/v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
