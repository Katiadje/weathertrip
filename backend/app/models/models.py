from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, CheckConstraint
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
    
    # Contraintes de sécurité
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(username)) >= 3", name="check_username_not_empty"),
        CheckConstraint("LENGTH(TRIM(email)) >= 5", name="check_email_not_empty"),
        CheckConstraint("LENGTH(password_hash) > 0", name="check_password_not_empty"),
    )
    
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
    
    # Contraintes de sécurité
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(name)) >= 3", name="check_trip_name_not_empty"),
    )
    
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
    
    # Contraintes de sécurité
    __table_args__ = (
        CheckConstraint("LENGTH(TRIM(city)) >= 2", name="check_city_not_empty"),
        CheckConstraint("LENGTH(TRIM(country)) >= 2", name="check_country_not_empty"),
        CheckConstraint("latitude >= -90 AND latitude <= 90", name="check_latitude_range"),
        CheckConstraint("longitude >= -180 AND longitude <= 180", name="check_longitude_range"),
    )
    
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
    weather_main = Column(String(100))
    weather_description = Column(String(255))
    icon = Column(String(10))
    wind_speed = Column(Float)
    clouds = Column(Integer)
    forecast_date = Column(DateTime)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Contraintes de sécurité
    __table_args__ = (
        CheckConstraint("humidity >= 0 AND humidity <= 100", name="check_humidity_range"),
        CheckConstraint("clouds >= 0 AND clouds <= 100", name="check_clouds_range"),
        CheckConstraint("wind_speed >= 0", name="check_wind_speed_positive"),
    )
    
    # Relations
    destination = relationship("Destination", back_populates="weather_data")