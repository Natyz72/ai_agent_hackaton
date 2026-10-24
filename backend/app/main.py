import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import demo, health, incidents, investigate
from app.config import settings

app = FastAPI(title="AI Suspicious Message Investigation Agent", version="0.1.0")

# Unified error responses matching frontend contract and tests
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": detail,
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": detail,
            },
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_err = exc.errors()[0]["msg"] if exc.errors() else "Validation error"
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "error": {
                "code": "VALIDATION_ERROR",
                "message": first_err,
            },
        },
    )


# CORS Middleware: credentials cannot be used with wildcard '*' origin
is_wildcard = "*" in settings.cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=not is_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(investigate.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")
app.include_router(demo.router, prefix="/api")

# Serve web/dist if present (Production single-service deployment)
web_dist = Path(__file__).resolve().parent.parent.parent / "web" / "dist"
if web_dist.exists():
    if (web_dist / "assets").exists():
        app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Don't interfere with API routes or interactive docs
        if full_path.startswith("api/") or full_path in ("docs", "redoc", "openapi.json"):
            raise HTTPException(status_code=404)

        # Serve static file if it exists in dist root (e.g., favicon.ico, robots.txt)
        file_path = web_dist / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)

        index_file = web_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        raise HTTPException(status_code=404)
else:
    @app.get("/")
    def root():
        return {"message": "AI Suspicious Message Investigation Agent API"}
