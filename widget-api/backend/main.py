"""
Widget-API Backend Microservice
Public API for serving eco-scores to widgets
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from routes.public_routes import router as public_router
from database.connection import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed

app = FastAPI(
    title="Widget-API Service",
    description="Public API for serving eco-scores and product data",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow all origins for widget embedding
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(public_router, prefix="/public", tags=["Public API"])

# Serve static files for React frontend (if built)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "react-app", "dist")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "widget-api"}

@app.get("/api/info")
async def api_info():
    """API information"""
    return {
        "name": "EcoLabel Widget API",
        "version": "1.0.0",
        "endpoints": {
            "get_product": "GET /public/product/{id}",
            "search_products": "GET /public/products/search",
            "get_score": "GET /public/score/{id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
