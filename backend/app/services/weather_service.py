import httpx
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from ..models import models
import unicodedata
COUNTRY_FR_TO_ISO2 = {
    "algerie": "DZ",
    "algérie": "DZ",
    "france": "FR",
    "espagne": "ES",
    "italie": "IT",
    "maroc": "MA",
    "tunisie": "TN",
    "belgique": "BE",
    "suisse": "CH",
    "allemagne": "DE",
    "royaume-uni": "GB",
    "angleterre": "GB",
    "etats-unis": "US",
    "états-unis": "US",
    "usa": "US",
    "canada": "CA",
}
def normalize_country_to_iso2(country: str) -> str:
    if not country:
        return ""

    c = country.strip()

    # Déjà un code ISO2 genre "IT"
    if len(c) == 2 and c.isalpha():
        return c.upper()

    # normalisation (enlève accents / casse)
    key = c.casefold()
    key = unicodedata.normalize("NFKD", key).encode("ascii", "ignore").decode("ascii")

    return COUNTRY_FR_TO_ISO2.get(key, c)


class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "YOUR_API_KEY_HERE")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
   
    async def get_current_weather(self, city: str, country: str = "") -> Optional[Dict]:
        """
        Récupère la météo actuelle pour une ville
        """
        country_code = normalize_country_to_iso2(country)
        location = f"{city},{country_code}" if country_code else city
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "fr"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Erreur lors de la récupération de la météo: {e}")
                return None
    
    async def get_forecast(self, city: str, country: str = "", days: int = 5) -> Optional[Dict]:
        """
        Récupère les prévisions météo pour une ville
        """
        country_code = normalize_country_to_iso2(country)
        location = f"{city},{country_code}" if country_code else city
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": "metric",
                        "lang": "fr"
                    },
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                print(f"Erreur lors de la récupération des prévisions: {e}")
                return None
    
    def save_weather_data(self, db: Session, destination_id: int, weather_data: Dict, forecast_date: Optional[datetime] = None):
        """
        Sauvegarde les données météo dans la base de données
        """
        weather_main = weather_data.get("weather", [{}])[0]
        main_data = weather_data.get("main", {})
        wind_data = weather_data.get("wind", {})
        clouds_data = weather_data.get("clouds", {})
        
        db_weather = models.WeatherData(
        destination_id=destination_id,
        temperature=main_data.get("temp"),
        feels_like=main_data.get("feels_like"),
        temp_min=main_data.get("temp_min"),
        temp_max=main_data.get("temp_max"),
        humidity=main_data.get("humidity"),
        weather_main=weather_main.get("main"),
        weather_description=weather_main.get("description"),
        icon=weather_main.get("icon"),
        wind_speed=wind_data.get("speed"),
        clouds=clouds_data.get("all"),
        forecast_date=forecast_date,          # ✅ une seule fois (None = current)
        fetched_at=datetime.utcnow()          # ✅ indispensable pour le cache
    )

        
        db.add(db_weather)
        db.commit()
        db.refresh(db_weather)
        return db_weather
    
    def get_cached_weather(self, db: Session, destination_id: int, max_age_hours: int = 1) -> Optional[models.WeatherData]:
        """
        Récupère les données météo en cache si elles sont récentes
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        return db.query(models.WeatherData).filter(
            models.WeatherData.destination_id == destination_id,
            models.WeatherData.fetched_at >= cutoff_time,
            models.WeatherData.forecast_date == None  # Données actuelles uniquement
        ).order_by(models.WeatherData.fetched_at.desc()).first()
    
    async def get_or_fetch_weather(self, db: Session, destination: models.Destination, force_refresh: bool = False):
        """
        Récupère la météo depuis le cache ou l'API
        """
        # Vérifier le cache d'abord
        if not force_refresh:
            cached = self.get_cached_weather(db, destination.id)
            if cached:
                return cached
        
        # Sinon, récupérer depuis l'API
        weather_data = await self.get_current_weather(destination.city, destination.country)
        
        if weather_data:
            return self.save_weather_data(db, destination.id, weather_data)
        
        return None
    
    async def fetch_and_save_forecast(self, db: Session, destination: models.Destination, days: int = 5):
        forecast_data = await self.get_forecast(destination.city, destination.country)

        if not forecast_data or "list" not in forecast_data:
            return []

        saved_forecasts = []
        points = min(len(forecast_data["list"]), days * 8)  # 8 points / jour (3h)
        for item in forecast_data["list"][:points]:
            forecast_time = datetime.fromtimestamp(item["dt"])
            forecast = self.save_weather_data(db, destination.id, item, forecast_time)
            saved_forecasts.append(forecast)

        return saved_forecasts


# Instance globale
weather_service = WeatherService()
