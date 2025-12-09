"""
Provenance Service - EcoLabel-MS2027
Data lineage tracking with DVC/MLflow integration
Port: 8006
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from database.connection import engine, Base
from routes.provenance_routes import router as provenance_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Provenance Service...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    logger.info("Shutting down Provenance Service...")


app = FastAPI(
    title="Provenance Service",
    description="Data lineage tracking with DVC/MLflow integration for EcoLabel-MS",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(provenance_router, prefix="/provenance", tags=["provenance"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "provenance"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Provenance Service",
        "version": "1.0.0",
        "description": "Data lineage tracking for EcoLabel-MS2027"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
