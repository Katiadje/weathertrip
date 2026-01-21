from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from datetime import datetime
from typing import Optional, List
import re

# ==================== VALIDATORS CUSTOM ====================

def validate_not_empty(v: str, field_name: str) -> str:
    """Valide qu'une chaîne n'est pas vide ou composée uniquement d'espaces"""
    if not v or not v.strip():
        raise ValueError(f"{field_name} ne peut pas être vide ou composé uniquement d'espaces")
    return v.strip()

def validate_no_sql_injection(v: str) -> str:
    """Détecte les tentatives d'injection SQL basiques"""
    dangerous_patterns = [
        r"(\bOR\b|\bAND\b).*=.*",
        r"(--|#|/\*|\*/)",
        r"(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b)",
        r"(UNION.*SELECT|SELECT.*FROM)"
    ]
    for pattern in dangerous_patterns:
        if re.search(pattern, v, re.IGNORECASE):
            raise ValueError("Contenu suspect détecté")
    return v

# ==================== USER SCHEMAS ====================

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Nom d'utilisateur")
    email: EmailStr = Field(..., description="Email valide")
    
    @field_validator('username')
    @classmethod
    def username_validator(cls, v):
        v = validate_not_empty(v, "Username")
        v = validate_no_sql_injection(v)
        
        # Uniquement alphanumériques, underscores, tirets
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Le username ne peut contenir que des lettres, chiffres, _ et -")
        
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="Mot de passe sécurisé")
    
    @field_validator('password')
    @classmethod
    def password_validator(cls, v):
        if not v or not v.strip():
            raise ValueError("Le mot de passe ne peut pas être vide")
        
        # Au moins 1 majuscule, 1 minuscule, 1 chiffre
        if not re.search(r'[A-Z]', v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        if not re.search(r'[a-z]', v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        if not re.search(r'\d', v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        
        return v

class UserLogin(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('username', 'password')
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Ce champ ne peut pas être vide")
        return v.strip()

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== DESTINATION SCHEMAS ====================

class DestinationBase(BaseModel):
    city: str = Field(..., min_length=2, max_length=100, description="Nom de la ville")
    country: str = Field(..., min_length=2, max_length=100, description="Nom du pays")
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    @field_validator('city', 'country')
    @classmethod
    def validate_location(cls, v, info):
        v = validate_not_empty(v, info.field_name.capitalize())
        v = validate_no_sql_injection(v)
        
        # Uniquement lettres, espaces, tirets, apostrophes
        if not re.match(r"^[a-zA-ZÀ-ÿ\s'-]+$", v):
            raise ValueError(f"{info.field_name.capitalize()} contient des caractères invalides")
        
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Vérifie que la date de départ est après la date d'arrivée"""
        if self.arrival_date and self.departure_date:
            if self.departure_date <= self.arrival_date:
                raise ValueError("La date de départ doit être supérieure à la date d'arrivée")
        return self

class DestinationCreate(DestinationBase):
    # ✅ FIX: nécessaire pour créer une destination via API/tests
    trip_id: int = Field(..., ge=1, description="ID du voyage")

class DestinationUpdate(BaseModel):
    city: Optional[str] = Field(None, min_length=2, max_length=100)
    country: Optional[str] = Field(None, min_length=2, max_length=100)
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    @field_validator('city', 'country')
    @classmethod
    def validate_location_update(cls, v, info):
        if v is not None:
            v = validate_not_empty(v, info.field_name.capitalize())
            v = validate_no_sql_injection(v)
            if not re.match(r"^[a-zA-ZÀ-ÿ\s'-]+$", v):
                raise ValueError(f"{info.field_name.capitalize()} contient des caractères invalides")
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Vérifie que la date de départ est après la date d'arrivée"""
        if self.arrival_date and self.departure_date:
            if self.departure_date <= self.arrival_date:
                raise ValueError("La date de départ doit être supérieure à la date d'arrivée")
        return self

class Destination(DestinationBase):
    id: int
    trip_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== TRIP SCHEMAS ====================

class TripBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=200, description="Nom du voyage")
    description: Optional[str] = Field(None, max_length=2000, description="Description")
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        v = validate_not_empty(v, "Nom du voyage")
        v = validate_no_sql_injection(v)
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is not None:
            v = v.strip()
            if not v:  # Si vide après strip, retourner None
                return None
            v = validate_no_sql_injection(v)
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Vérifie que la date de fin est après la date de début"""
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("La date de fin doit être supérieure à la date de début")
        return self

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    @field_validator('name')
    @classmethod
    def validate_name_update(cls, v):
        if v is not None:
            v = validate_not_empty(v, "Nom du voyage")
            v = validate_no_sql_injection(v)
        return v
    
    @field_validator('description')
    @classmethod
    def validate_description_update(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                return None
            v = validate_no_sql_injection(v)
        return v
    
    @model_validator(mode='after')
    def validate_dates(self):
        """Vérifie que la date de fin est après la date de début"""
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("La date de fin doit être supérieure à la date de début")
        return self

class Trip(TripBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    destinations: List[Destination] = []
    
    class Config:
        from_attributes = True

# ==================== WEATHER SCHEMAS ====================

class WeatherDataBase(BaseModel):
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    humidity: Optional[int] = Field(None, ge=0, le=100)
    weather_main: Optional[str] = None
    weather_description: Optional[str] = None
    icon: Optional[str] = None
    wind_speed: Optional[float] = Field(None, ge=0)
    clouds: Optional[int] = Field(None, ge=0, le=100)
    forecast_date: Optional[datetime] = None

class WeatherData(WeatherDataBase):
    id: int
    destination_id: int
    fetched_at: datetime
    
    class Config:
        from_attributes = True

class WeatherResponse(BaseModel):
    destination: Destination
    current_weather: Optional[WeatherData] = None
    forecast: List[WeatherData] = []
