"""
AI Resume Analyzer — FastAPI entry point.

Run from the backend folder:
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routes import analyze, health, report, upload
from app.services.storage import init_db

app = FastAPI(
    title=settings.app_name,
    description="Analyze resumes, estimate ATS compatibility, and compare against job descriptions.",
    version="1.0.0",
)

# Allow local Vite dev server (and common localhost variants)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(report.router)


@app.on_event("startup")
def on_startup():
    init_db()


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Never expose Python stack traces to API clients."""
    # Let FastAPI handle intentional HTTP errors (400/404/422, etc.)
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected server error occurred. Please try again."},
    )


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "message": "API is running. Visit /docs for interactive documentation.",
        "health": "/api/health",
    }
