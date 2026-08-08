"""FastAPI application factory, middleware, and router registration."""
import time
from collections import defaultdict
from typing import Dict, List
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import settings
from src.db.database import init_db
from src.api.routes.auth import router as auth_router
from src.api.routes.chat import router as chat_router
from src.api.routes.orders import router as orders_router
from src.api.routes.tickets import router as tickets_router
from src.api.routes.feedback import router as feedback_router
from src.api.routes.admin import router as admin_router
from src.utils.logger import logger

# Simple in-memory sliding rate limiter per IP
_rate_limit_records: Dict[str, List[float]] = defaultdict(list)


def create_app() -> FastAPI:
    """Constructs and configures the FastAPI application instance."""
    app = FastAPI(
        title="SupportFlow AI — Customer Support API",
        description="Production backend for SupportFlow AI agentic support platform.",
        version="0.3.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 1. CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 2. Rate Limiting Middleware
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        window = 60.0  # 60 seconds

        # Clean timestamps older than 60s
        timestamps = [ts for ts in _rate_limit_records[client_ip] if now - ts < window]
        _rate_limit_records[client_ip] = timestamps

        if len(timestamps) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Too many requests. Rate limit is 60 requests per minute."},
            )

        _rate_limit_records[client_ip].append(now)
        response = await call_next(request)
        return response

    # 3. Router Registration
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(orders_router)
    app.include_router(tickets_router)
    app.include_router(feedback_router)
    app.include_router(admin_router)

    # 4. Health Check Endpoint
    @app.get("/api/health", tags=["Health"])
    def health_check():
        return {
            "status": "healthy",
            "environment": settings.ENVIRONMENT,
            "version": "0.3.0",
            "database": settings.DATABASE_URL.split("://")[0],
        }

    # 5. Startup Hook
    @app.on_event("startup")
    def on_startup():
        logger.info("Starting SupportFlow AI FastAPI application...")
        init_db()

    return app


app = create_app()
