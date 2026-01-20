from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Destination Schemas
class DestinationBase(BaseModel):
    city: str
    country: str
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class DestinationCreate(DestinationBase):
    pass

class DestinationUpdate(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    arrival_date: Optional[datetime] = None
    departure_date: Optional[datetime] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Destination(DestinationBase):
    id: int
    trip_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Trip Schemas
class TripBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class Trip(TripBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    destinations: List[Destination] = []
    
    class Config:
        from_attributes = True

# Weather Schemas
class WeatherDataBase(BaseModel):
    temperature: Optional[float] = None
    feels_like: Optional[float] = None
    temp_min: Optional[float] = None
    temp_max: Optional[float] = None
    humidity: Optional[int] = None
    weather_main: Optional[str] = None
    weather_description: Optional[str] = None
    icon: Optional[str] = None
    wind_speed: Optional[float] = None
    clouds: Optional[int] = None
    forecast_date: Optional[datetime] = None

class WeatherData(WeatherDataBase):
    id: int
    destination_id: int
    fetched_at: datetime
    
    class Config:
        from_attributes = True

# Response schemas
class WeatherResponse(BaseModel):
    destination: Destination
    current_weather: Optional[WeatherData] = None
    forecast: List[WeatherData] = []
