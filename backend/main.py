"""
DREAM AI - FastAPI Main Application
Entry point for the backend API server
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# Import routers
from api.deals import deals_router
from api.documents import documents_router
from api.extraction import extraction_router, deals_extraction_router
from api.endpoints import (
    analyses_router,
    markets_router,
    reports_router,
    tasks_router,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DREAM AI API",
    description="Deal intake and document processing API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (configure for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(deals_router)
app.include_router(documents_router)
app.include_router(extraction_router)
app.include_router(deals_extraction_router)
app.include_router(analyses_router)
app.include_router(markets_router)
app.include_router(reports_router)
app.include_router(tasks_router)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "DREAM AI API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


