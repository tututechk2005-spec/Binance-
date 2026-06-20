from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import time

from core.config import settings
from core.database import engine, Base
from core.redis_client import redis_client
from api.auth.router import router as auth_router
from api.users.router import router as users_router
from api.trades.router import router as trades_router
from api.signals.router import router as signals_router
from api.portfolio.router import router as portfolio_router
from api.payments.router import router as payments_router
from api.notifications.router import router as notifications_router
from api.admin.router import router as admin_router
from api.websocket.router import router as ws_router
from middleware.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Binance AI Trader Pro API...")
    await redis_client.connect()
    logger.info("Redis connected.")
    yield
    await redis_client.disconnect()
    logger.info("Shutting down API...")


app = FastAPI(
    title="Binance AI Trader Pro API",
    description="Professional AI-powered Binance trading platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} → {response.status_code}")
    return response


app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users_router, prefix="/api/users", tags=["Users"])
app.include_router(trades_router, prefix="/api/trades", tags=["Trades"])
app.include_router(signals_router, prefix="/api/signals", tags=["AI Signals"])
app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(payments_router, prefix="/api/payments", tags=["Payments"])
app.include_router(notifications_router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(admin_router, prefix="/api/admin", tags=["Admin"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])


@app.get("/api/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Binance AI Trader Pro",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
