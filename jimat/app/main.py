"""
Main FastAPI application entry point.

This file:
1. Creates the FastAPI app
2. Includes all routers (endpoints)
3. Creates database tables on startup
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from jimat.app.core.config import settings
from jimat.app.database.session import engine
from jimat.app.models import Base
from jimat.app.api.v1.routes import categories, expenses
import json


# Create database tables if they don't exist
# This runs once on startup
Base.metadata.create_all(bind=engine)


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="An API for tracking monthly expenses with categories",
    version="1.0.0"
)


# Add CORS middleware
# Why CORS: Allows requests from your Next.js frontend (different origin)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Log detailed validation errors"""
    print(f"\n=== VALIDATION ERROR ===")
    print(f"Path: {request.url.path}")
    print(f"Method: {request.method}")
    errors = exc.errors()
    print(f"Raw errors: {json.dumps(errors, indent=2)}")
    
    # Try to log the request body if available
    try:
        body = await request.body()
        print(f"Request body: {body.decode() if body else 'empty'}")
    except:
        pass
    
    print(f"======================\n")
    
    return JSONResponse(
        status_code=422,
        content={"detail": errors},
    )


# Include routers (endpoints)
# This mounts the category and expense routes under /api/v1
app.include_router(categories.router, prefix="/api/v1")
app.include_router(expenses.router, prefix="/api/v1")


# Root endpoint (health check)
@app.get("/", tags=["health"])
def root():
    """Welcome endpoint"""
    return {"message": "Welcome to Expense Tracker API", "status": "running"}


@app.get("/health", tags=["health"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
