import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import health, investigate, incidents

app = FastAPI(title="AI Suspicious Message Investigation Agent", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(investigate.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")

# Serve web/dist if present (Render deployment)
web_dist = Path(__file__).resolve().parent.parent.parent / "web" / "dist"
if web_dist.exists():
    app.mount("/assets", StaticFiles(directory=web_dist / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Don't interfere with API routes
        if full_path.startswith("api/"):
            from fastapi import HTTPException

            raise HTTPException(status_code=404)
        index_file = web_dist / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        from fastapi import HTTPException

        raise HTTPException(status_code=404)
else:
    @app.get("/")
    def root():
        return {"message": "AI Suspicious Message Investigation Agent API"}
