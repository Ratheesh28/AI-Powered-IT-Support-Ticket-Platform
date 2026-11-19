"""FastAPI application entry point.

Run locally:  uvicorn app.main:app --reload
Interactive docs: http://127.0.0.1:8000/docs
"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (importing registers the tables with SQLAlchemy)
from app.config import settings
from app.database import Base, engine
from app.predictor import ModelNotLoadedError, predictor
from app.routes import router

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Runs once at startup (before `yield`) and once at shutdown (after)."""
    max_retries = 3
    retry_delay = 2  # seconds between attempts to allow serverless compute wake-up

    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("Database tables initialized successfully (attempt %d/%d).", attempt, max_retries)
            break
        except Exception:
            logger.exception("Database initialization failed on attempt %d/%d.", attempt, max_retries)
            if attempt < max_retries:
                await asyncio.sleep(retry_delay)
            else:
                logger.error(
                    "All %d database connection attempts failed during startup. "
                    "Starting application in degraded mode.",
                    max_retries,
                )

    predictor.load()
    yield


app = FastAPI(
    title="AI-Powered IT Support Ticket Intelligence Platform",
    description="Classifies IT support tickets (Network, Hardware, Software, Account Access). "
    "The bundled dataset is SYNTHETIC DEMO data.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS: lets a browser frontend on another origin (e.g. React on :3000) call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000
    logger.info("%s %s -> %s (%.1f ms)", request.method, request.url.path, response.status_code, elapsed_ms)
    return response


@app.exception_handler(ModelNotLoadedError)
async def model_not_loaded_handler(request: Request, exc: ModelNotLoadedError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Full traceback goes to the log; the client gets a safe, generic message.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


app.include_router(router)
