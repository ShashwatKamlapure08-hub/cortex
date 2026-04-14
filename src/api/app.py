# src/api/app.py
# Cortex — Main FastAPI Application
# Entry point for the Cortex API server

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

# --- App Setup ---

app = FastAPI(
    title="Cortex Script Engine API",
    description=(
        "Cortex is a multi-format AI script generation engine. "
        "Generate production-ready scripts for YouTube Shorts, "
        "medium videos, and long-form podcasts."
    ),
    version="1.0.0",
    docs_url="/docs",       # Swagger UI at /docs
    redoc_url="/redoc"      # ReDoc UI at /redoc
)

# --- CORS Middleware ---
# Allows any frontend app to call the Cortex API

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Include Routes ---

app.include_router(router, prefix="/api/v1")


# --- Root Endpoint ---

@app.get("/")
def root():
    return {
        "service": "Cortex Script Engine",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "generate": "/api/v1/generate",
            "formats": "/api/v1/formats"
        }
    }
