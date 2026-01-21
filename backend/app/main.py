from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import time
from sqlalchemy import text

from .database.database import engine, Base
from .routes import users, trips, destinations, weather

from .middleware import (
    setup_csrf_protection,
    setup_rate_limiting,
    limiter,
    setup_security_headers,
)
from .middleware.auth import setup_brute_force_protection


app = FastAPI(
    title="WeatherTrip API",
    description="API de gestion de voyages avec intégration météo - Version Sécurisée",
    version="2.0.0"
)

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
    max_age=600,
)

# Security
environment = os.getenv("ENVIRONMENT", "development")
setup_security_headers(app, environment=environment)

secret_key = os.getenv("SECRET_KEY", "change-me")
setup_csrf_protection(app, secret_key=secret_key)

setup_rate_limiting(app)
setup_brute_force_protection(app, login_endpoints=["/users/login"])

# Routes
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(destinations.router)
app.include_router(weather.router)

# FRONT (force Docker path)
FRONTEND_DIR = os.getenv("FRONTEND_DIR", "/app/frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
INDEX_FILE = os.path.join(FRONTEND_DIR, "templates", "index.html")

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def wait_for_db_and_init(max_wait_seconds: int = 60):
    deadline = time.time() + max_wait_seconds
    last_error = None
    while time.time() < deadline:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            print("✅ DB ready + tables initialized")
            return
        except Exception as e:
            last_error = e
            print(f"⏳ Waiting for DB... ({e})")
            time.sleep(2)
    raise RuntimeError(f"DB not ready after {max_wait_seconds}s: {last_error}")


@app.on_event("startup")
def on_startup():
    wait_for_db_and_init(60)
    print(f"✅ FRONTEND_DIR={FRONTEND_DIR}")
    print(f"✅ INDEX_FILE={INDEX_FILE}")
    print(f"✅ index exists={os.path.exists(INDEX_FILE)}")


@app.get("/", include_in_schema=False)
async def root():
    if os.path.exists(INDEX_FILE):
        return FileResponse(INDEX_FILE)
    return {"error": "Frontend not found", "index_file": INDEX_FILE, "exists": os.path.exists(INDEX_FILE)}


@app.get("/health", include_in_schema=False)
@limiter.limit("60/minute")
async def health_check(request: Request):
    return {"status": "ok"}
