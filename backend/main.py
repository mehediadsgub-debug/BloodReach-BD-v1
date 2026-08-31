"""
╔══════════════════════════════════════════════════════════════╗
║         BloodReach BD — FastAPI Application Entry             ║
║                                                              ║
║  Auth endpoints:                                             ║
║    POST /api/v1/auth/login                                   ║
║    POST /api/v1/auth/register                                ║
║    POST /api/v1/auth/refresh                                 ║
║    GET  /api/v1/auth/me                                      ║
║    POST /api/v1/auth/logout                                  ║
║                                                              ║
║  Location endpoints:                                         ║
║    GET  /api/v1/locations/divisions                          ║
║    GET  /api/v1/locations/districts/{division_id}            ║
╚══════════════════════════════════════════════════════════════╝
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import init_db
from app.routes.auth import router as auth_router
from app.routes.locations import router as locations_router
from app.routes.users import router as users_router
from app.routes.requests import router as requests_router
from app.routes.donors import router as donors_router
from app.routes.hospitals import router as hospitals_router
from app.routes.notifications import router as notifications_router
from app.routes.analytics import router as analytics_router
from app.routes.admin import router as admin_router
from app.services.scheduler_service import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & shutdown events"""
    # Startup: ensure tables exist (won't drop existing data)
    try:
        init_db()
        print("[OK] Database tables verified / created")
    except Exception as e:
        print(f"[WARN] Database initialization warning: {e}")

    # Start background scheduler
    try:
        start_scheduler()
        print("[OK] Background scheduler started (escalation & low stock)")
    except Exception as e:
        print(f"[WARN] Could not start scheduler: {e}")

    yield

    # Shutdown: cleanup scheduler
    try:
        stop_scheduler()
        print("[OK] Background scheduler stopped")
    except Exception:
        pass
    print("[OK] Application shutting down")


app = FastAPI(
    title="BloodReach BD API",
    description="Bangladesh real-time blood availability & donor matching platform covering all 64 districts",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS — allow frontend on any port (3000, 5500, 8000, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

import os
from fastapi.staticfiles import StaticFiles

# ── Register Routers ─────────────────────────────────────
app.include_router(auth_router)
app.include_router(locations_router)
app.include_router(users_router)
app.include_router(requests_router)
app.include_router(donors_router)
app.include_router(hospitals_router)
app.include_router(notifications_router)
app.include_router(analytics_router)
app.include_router(admin_router)


from fastapi import WebSocket, WebSocketDisconnect, Query, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.websocket_manager import ws_manager
from app.services.auth_service import get_user_from_token


@app.websocket("/ws/notifications")
async def websocket_notifications(
    websocket: WebSocket,
    token: str = Query(...)
):
    """Real-time WebSocket endpoint for instant in-app alerts and notifications"""
    try:
        user_info = get_user_from_token(token)
        if not user_info:
            await websocket.close(code=1008)  # Policy violation / unauthorized
            return
        user_id_str = str(user_info["user_id"])
    except Exception:
        await websocket.close(code=1008)
        return

    await ws_manager.connect(user_id_str, websocket)
    try:
        # Keep connection open and receive heartbeat pings
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        await ws_manager.disconnect(user_id_str, websocket)
    except Exception:
        await ws_manager.disconnect(user_id_str, websocket)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "running",
        "app": "BloodReach BD",
        "version": "1.0.0",
        "districts_covered": 64,
        "divisions_covered": 8,
        "websocket": "enabled"
    }


# ── Mount Frontend Static Files & Routes ───────────────────
from fastapi.responses import FileResponse, HTMLResponse

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

# Mount assets directory
assets_dir = os.path.join(FRONTEND_DIR, "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse("<h1>BloodReach BD</h1><p>Frontend file not found</p>")

@app.get("/{page}.html", response_class=HTMLResponse)
async def serve_html_page(page: str):
    path = os.path.join(FRONTEND_DIR, f"{page}.html")
    if os.path.exists(path):
        return FileResponse(path)
    return HTMLResponse(status_code=404, content="<h1>404 — Page Not Found</h1>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



