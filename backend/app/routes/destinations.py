from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database.database import get_db
from ..models import models, schemas

router = APIRouter(prefix="/destinations", tags=["destinations"])

@router.post("/", response_model=schemas.Destination, status_code=status.HTTP_201_CREATED)
def create_destination(destination: schemas.DestinationCreate, trip_id: int, db: Session = Depends(get_db)):
    """Ajoute une destination à un voyage"""
    # Vérifier que le voyage existe
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    
    db_destination = models.Destination(
        city=destination.city,
        country=destination.country,
        arrival_date=destination.arrival_date,
        departure_date=destination.departure_date,
        latitude=destination.latitude,
        longitude=destination.longitude,
        trip_id=trip_id
    )
    
    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)
    
    return db_destination

@router.get("/trip/{trip_id}", response_model=List[schemas.Destination])
def get_destinations_by_trip(trip_id: int, db: Session = Depends(get_db)):
    """Récupère toutes les destinations d'un voyage"""
    destinations = db.query(models.Destination).filter(
        models.Destination.trip_id == trip_id
    ).all()
    
    return destinations

@router.get("/{destination_id}", response_model=schemas.Destination)
def get_destination(destination_id: int, db: Session = Depends(get_db)):
    """Récupère une destination par son ID"""
    destination = db.query(models.Destination).filter(
        models.Destination.id == destination_id
    ).first()
    
    if not destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")
    
    return destination

@router.put("/{destination_id}", response_model=schemas.Destination)
def update_destination(
    destination_id: int, 
    destination_update: schemas.DestinationUpdate, 
    db: Session = Depends(get_db)
):
    """Met à jour une destination"""
    db_destination = db.query(models.Destination).filter(
        models.Destination.id == destination_id
    ).first()
    
    if not db_destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")
    
    # Mettre à jour les champs fournis
    update_data = destination_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_destination, field, value)
    
    db.commit()
    db.refresh(db_destination)
    
    return db_destination

@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(destination_id: int, db: Session = Depends(get_db)):
    """Supprime une destination"""
    db_destination = db.query(models.Destination).filter(
        models.Destination.id == destination_id
    ).first()
    
    if not db_destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")
    
    db.delete(db_destination)
    db.commit()
    
    return None
