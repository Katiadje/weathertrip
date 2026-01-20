from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")

class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    user = relationship("User", back_populates="trips")
    destinations = relationship("Destination", back_populates="trip", cascade="all, delete-orphan")

class Destination(Base):
    __tablename__ = "destinations"
    
    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(200), nullable=False)
    country = Column(String(100), nullable=False)
    arrival_date = Column(DateTime)
    departure_date = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    trip = relationship("Trip", back_populates="destinations")
    weather_data = relationship("WeatherData", back_populates="destination", cascade="all, delete-orphan")

class WeatherData(Base):
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    destination_id = Column(Integer, ForeignKey("destinations.id"), nullable=False)
    temperature = Column(Float)
    feels_like = Column(Float)
    temp_min = Column(Float)
    temp_max = Column(Float)
    humidity = Column(Integer)
    weather_main = Column(String(100))  # Ex: Clear, Rain, Clouds
    weather_description = Column(String(255))
    icon = Column(String(10))
    wind_speed = Column(Float)
    clouds = Column(Integer)
    forecast_date = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    destination = relationship("Destination", back_populates="weather_data")
