from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database.database import engine, Base
from .routes import users, trips, destinations, weather

# 🔐 Import des middlewares de sécurité
from .middleware import (
    setup_csrf_protection,
    setup_rate_limiting,
    limiter,
    setup_security_headers,
)
from .middleware.auth import setup_brute_force_protection

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title="WeatherTrip API",
    description="API de gestion de voyages avec intégration météo - Version Sécurisée",
    version="2.0.0"
)

# 🔐 SÉCURITÉ : Configuration CORS restrictive
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # ⚠️ Plus de "*" !
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],  # Ajout X-CSRF-Token
    max_age=600,
)

# 🔐 SÉCURITÉ : Headers de sécurité HTTP
environment = os.getenv("ENVIRONMENT", "development")
setup_security_headers(app, environment=environment)

# 🔐 SÉCURITÉ : Protection CSRF
secret_key = os.getenv("SECRET_KEY", "super_secret_key_change_in_production")
setup_csrf_protection(app, secret_key=secret_key)

# 🔐 SÉCURITÉ : Rate Limiting
setup_rate_limiting(app)

# 🔐 SÉCURITÉ : Protection anti-brute force
setup_brute_force_protection(app, login_endpoints=["/users/login"])

# Inclure les routes
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(destinations.router)
app.include_router(weather.router)

# Servir les fichiers statiques (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    static_path = os.path.join(frontend_path, "static")
    if os.path.exists(static_path):
        app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def root():
    """Page d'accueil - servir le frontend"""
    frontend_index = os.path.join(frontend_path, "templates", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {
        "message": "Bienvenue sur WeatherTrip API - Version Sécurisée",
        "version": "2.0.0",
        "docs": "/docs"
    }

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Endpoint de santé"""
    return {
        "status": "healthy",
        "message": "WeatherTrip API is running",
        "version": "2.0.0",
        "security": "enabled"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)