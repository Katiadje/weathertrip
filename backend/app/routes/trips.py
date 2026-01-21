from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import ValidationError

from ..database.database import get_db
from ..models import models, schemas

router = APIRouter(prefix="/trips", tags=["trips"])

@router.post("/", response_model=schemas.Trip, status_code=status.HTTP_201_CREATED)
def create_trip(trip: schemas.TripCreate, user_id: int, db: Session = Depends(get_db)):
    """
    Crée un nouveau voyage avec validation stricte
    """
    try:
        # Vérifier que l'utilisateur existe
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # Nettoyer et valider les données
        db_trip = models.Trip(
            name=trip.name.strip(),
            description=trip.description.strip() if trip.description else None,
            start_date=trip.start_date,
            end_date=trip.end_date,
            user_id=user_id
        )
        
        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        
        return db_trip
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la création du voyage")

@router.get("/", response_model=List[schemas.Trip])
def get_trips(user_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Récupère tous les voyages d'un utilisateur
    """
    if limit > 100:
        limit = 100  # Protection contre les requêtes trop larges
    
    trips = db.query(models.Trip).filter(
        models.Trip.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    return trips

@router.get("/{trip_id}", response_model=schemas.Trip)
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    """
    Récupère un voyage par son ID
    """
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    
    if not trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    
    return trip

@router.put("/{trip_id}", response_model=schemas.Trip)
def update_trip(trip_id: int, trip_update: schemas.TripUpdate, db: Session = Depends(get_db)):
    """
    Met à jour un voyage avec validation
    """
    try:
        db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
        
        if not db_trip:
            raise HTTPException(status_code=404, detail="Voyage non trouvé")
        
        # Mettre à jour les champs fournis avec nettoyage
        update_data = trip_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ['name', 'description'] and value:
                value = value.strip()
                if not value and field == 'name':  # name ne peut pas être vide
                    raise HTTPException(status_code=422, detail="Le nom ne peut pas être vide")
            setattr(db_trip, field, value)
        
        db.commit()
        db.refresh(db_trip)
        
        return db_trip
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")

@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    """
    Supprime un voyage
    """
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    
    if not db_trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    
    db.delete(db_trip)
    db.commit()
    
    return None