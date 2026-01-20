from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models import models, schemas
from ..services.weather_service import weather_service

router = APIRouter(prefix="/weather", tags=["weather"])

@router.get("/destination/{destination_id}", response_model=schemas.WeatherResponse)
async def get_destination_weather(
    destination_id: int, 
    force_refresh: bool = Query(False, description="Forcer la récupération depuis l'API"),
    db: Session = Depends(get_db)
):
    """
    Récupère la météo pour une destination
    Utilise le cache si disponible, sinon fait un appel à l'API
    """
    # Récupérer la destination
    destination = db.query(models.Destination).filter(
        models.Destination.id == destination_id
    ).first()
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")
    
    # Récupérer la météo actuelle
    current_weather = await weather_service.get_or_fetch_weather(db, destination, force_refresh)
    
    # Récupérer les prévisions depuis la DB (si elles existent)
    forecast = db.query(models.WeatherData).filter(
    models.WeatherData.destination_id == destination_id,
    models.WeatherData.forecast_date.isnot(None)
    ).order_by(models.WeatherData.forecast_date).limit(40).all()
        
    return schemas.WeatherResponse(
        destination=destination,
        current_weather=current_weather,
        forecast=forecast
    )

@router.post("/destination/{destination_id}/forecast")
async def fetch_forecast(destination_id: int, db: Session = Depends(get_db)):
    """
    Force la récupération des prévisions météo pour une destination
    """
    # Récupérer la destination
    destination = db.query(models.Destination).filter(
        models.Destination.id == destination_id
    ).first()
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")
    
    # Supprimer les anciennes prévisions
    db.query(models.WeatherData).filter(
    models.WeatherData.destination_id == destination_id,
    models.WeatherData.forecast_date.isnot(None)
    ).delete(synchronize_session=False)
    db.commit()

    # Récupérer les nouvelles prévisions
    forecasts = await weather_service.fetch_and_save_forecast(db, destination)
    
    return {
        "message": "Prévisions récupérées avec succès",
        "count": len(forecasts),
        "forecasts": forecasts
    }

@router.get("/trip/{trip_id}")
async def get_trip_weather(trip_id: int, db: Session = Depends(get_db)):
    """
    Récupère la météo pour toutes les destinations d'un voyage
    """
    # Récupérer le voyage
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    
    # Récupérer les destinations
    destinations = db.query(models.Destination).filter(
        models.Destination.trip_id == trip_id
    ).all()
    
    # Récupérer la météo pour chaque destination
    results = []
    for destination in destinations:
        current_weather = await weather_service.get_or_fetch_weather(db, destination, False)
        
        results.append({
            "destination": destination,
            "current_weather": current_weather
        })
    
    return {
        "trip": trip,
        "destinations_weather": results
    }

@router.get("/city/{city}")
async def get_city_weather(
    city: str, 
    country: str = Query("", description="Code pays (optionnel)")
):
    """
    Recherche la météo pour une ville (sans l'enregistrer)
    Utile pour la recherche avant d'ajouter une destination
    """
    weather_data = await weather_service.get_current_weather(city, country)
    
    if not weather_data:
        raise HTTPException(
            status_code=404, 
            detail=f"Impossible de récupérer la météo pour {city}"
        )
    
    return weather_data
