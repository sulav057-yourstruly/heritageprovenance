"""
FastAPI main application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.db import init_db
from app.routes import router  # Original provenance routes
from app.routes_auth import router as auth_router
from app.routes_gallery import router as gallery_router
from app.routes_contribute import router as contribute_router
from app.routes_contributor import router as contributor_router
from app.routes_admin import router as admin_router

app = FastAPI(
    title="Kathmandu Cultural Heritage Archive API",
    description="Digital heritage provenance tracking system with trust-based contribution model",
    version="1.0.0"
)

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)  # Original provenance routes
app.include_router(auth_router)
app.include_router(gallery_router)
app.include_router(contribute_router)
app.include_router(contributor_router)
app.include_router(admin_router)

# Serve uploaded images under /data/*
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

@app.get("/")
async def root():
    return {"message": "Provenance API", "version": "0.1.0"}

@app.get("/health")
async def health():
    return {"status": "ok"}

