"""
FastAPI Application Entry Point

This module initializes the FastAPI application with all necessary configurations,
middleware, routers, and exception handlers.
"""

import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api import articles, crawler, statistics, health
from backend.config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT,
)

logger = logging.getLogger(__name__)


# Custom middleware for request timeout and size limit
class RequestMiddleware(BaseHTTPMiddleware):
    """Custom middleware for request handling"""

    async def dispatch(self, request: Request, call_next):
        """Process request with timeout and size limit"""
        # Check request size
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > settings.MAX_REQUEST_SIZE:
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "message": f"Request body too large. Maximum size is {settings.MAX_REQUEST_SIZE} bytes"
                },
            )

        # Add request timing
        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log request
            logger.info(
                "%s %s - Status: %s - Time: %.3fs",
                request.method,
                request.url.path,
                response.status_code,
                process_time,
            )

            # Add timing header
            response.headers["X-Process-Time"] = str(process_time)
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "%s %s - Error: %s - Time: %.3fs",
                request.method,
                request.url.path,
                str(e),
                process_time,
                exc_info=True,
            )
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifespan events"""
    # Startup
    logger.info("Starting %s v%s", settings.API_TITLE, settings.API_VERSION)
    logger.info("Elasticsearch: %s:%s", settings.ELASTICSEARCH_HOST, settings.ELASTICSEARCH_PORT)
    logger.info("CORS Origins: %s", settings.CORS_ORIGINS)
    yield
    # Shutdown
    logger.info("Shutting down %s", settings.API_TITLE)


# Initialize FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)


# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time"],
)


# Add custom request middleware
app.add_middleware(RequestMiddleware)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors"""
    logger.warning(
        "Validation error for %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "details": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    logger.error(
        "Unhandled exception for %s %s: %s",
        request.method,
        request.url.path,
        str(exc),
        exc_info=True,
    )

    # In production, hide sensitive error details
    if settings.LOG_LEVEL == "DEBUG":
        error_detail = str(exc)
    else:
        error_detail = "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": error_detail,
        },
    )


# Register routers
app.include_router(
    articles.router,
    prefix="/api/articles",
    tags=["articles"],
)

app.include_router(
    crawler.router,
    prefix="/api/crawler",
    tags=["crawler"],
)

app.include_router(
    statistics.router,
    prefix="/api/statistics",
    tags=["statistics"],
)

app.include_router(
    health.router,
    tags=["health"],
)


# Root endpoint
@app.get("/", tags=["root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower(),
    )
