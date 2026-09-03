import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.database import init_db
from app.core.config import settings
from app.scheduler.jobs import start_scheduler, shutdown_scheduler

from app.api import auth, dashboard, employees, courses, learning, certificates, automation, settings_api

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("Database initialized")
    start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(
    title="Smart Certificate Generator API",
    description="Automatically monitors employee learning progress and issues certificates when targets are reached.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Global error handling: never leak internals to the client ---

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Invalid request data", "errors": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error on %s %s: %s", request.method, request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# --- Routers ---
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(employees.router)
app.include_router(courses.router)
app.include_router(learning.router)
app.include_router(certificates.router)
app.include_router(automation.router)
app.include_router(settings_api.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "Smart Certificate Generator API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
