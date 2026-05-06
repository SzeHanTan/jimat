"""
Jimat AI Service - Main FastAPI Application

Multi-domain AI microservice for intelligent expense tracking, 
insurance claims processing, and financial insights using 
LangChain/LangGraph orchestration.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
from datetime import datetime
import time

from app.core.config import get_settings
from app.api.v1.routes import documents, categorization

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="Multi-agent AI orchestration service for domain-specific intelligence",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "http://127.0.0.1:3000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Trusted Host middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "testserver"]
)


# Include routers
app.include_router(documents.router)
app.include_router(categorization.router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    request_id = request.headers.get("X-Request-ID", f"req-{int(time.time() * 1000)}")
    
    logger.info(f"[{request_id}] {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(
            f"[{request_id}] {request.method} {request.url.path} - "
            f"Status: {response.status_code} - Duration: {process_time:.3f}s"
        )
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"[{request_id}] Error: {str(e)} - Duration: {process_time:.3f}s")
        raise


# Root endpoint
@app.get("/")
async def root():
    """Service information and status"""
    return {
        "service": settings.app_name,
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "llm_provider": settings.llm_provider,
        "docs": "/docs",
        "health": "/health"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "timestamp": datetime.now().isoformat(),
        "uptime": "running"
    }


# Error handler for exceptions
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc) if settings.debug else "An error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"LLM Provider: {settings.llm_provider}")
    logger.info(f"Debug Mode: {settings.debug}")
    
    # Test LLM configuration (optional)
    if settings.llm_provider == "huggingface":
        if not settings.hf_api_key:
            logger.warning("HF_API_KEY not set. Hugging Face features will not work.")
        else:
            logger.info(f"HF Model: {settings.hf_model}")
    
    logger.info(f"Service ready at http://localhost:{settings.port}")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.app_name}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
