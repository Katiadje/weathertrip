from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from .database.database import engine, Base
from .routes import users, trips, destinations, weather

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title="WeatherTrip API",
    description="API de gestion de voyages avec intégration météo",
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les origines autorisées
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes
app.include_router(users.router)
app.include_router(trips.router)
app.include_router(destinations.router)
app.include_router(weather.router)

# Servir les fichiers statiques (frontend)
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_path, "static")), name="static")

@app.get("/")
async def root():
    """Page d'accueil - servir le frontend"""
    frontend_index = os.path.join(frontend_path, "templates", "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "Bienvenue sur WeatherTrip API"}

@app.get("/health")
async def health_check():
    """Endpoint de santé"""
    return {"status": "healthy", "message": "WeatherTrip API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
