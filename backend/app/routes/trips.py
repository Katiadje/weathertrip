from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from pydantic import ValidationError

from ..database.database import get_db
from ..models import models, schemas
from ..services import auth_service

router = APIRouter(prefix="/trips", tags=["trips"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    user = auth_service.get_current_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/", response_model=schemas.Trip, status_code=status.HTTP_201_CREATED)
def create_trip(
    trip: schemas.TripCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Crée un nouveau voyage pour l'utilisateur connecté
    """
    try:
        db_trip = models.Trip(
            name=trip.name.strip(),
            description=trip.description.strip() if trip.description else None,
            start_date=trip.start_date,
            end_date=trip.end_date,
            user_id=current_user.id,
        )

        db.add(db_trip)
        db.commit()
        db.refresh(db_trip)
        return db_trip

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la création du voyage")


@router.get("/", response_model=List[schemas.Trip])
def get_trips(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Récupère tous les voyages de l'utilisateur connecté
    """
    if limit > 100:
        limit = 100

    trips = (
        db.query(models.Trip)
        .filter(models.Trip.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return trips


@router.get("/{trip_id}", response_model=schemas.Trip)
def get_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")
    return trip


@router.put("/{trip_id}", response_model=schemas.Trip)
def update_trip(
    trip_id: int,
    trip_update: schemas.TripUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
        if not db_trip:
            raise HTTPException(status_code=404, detail="Voyage non trouvé")
        if db_trip.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit")

        update_data = trip_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["name", "description"] and value:
                value = value.strip()
                if not value and field == "name":
                    raise HTTPException(status_code=422, detail="Le nom ne peut pas être vide")
            setattr(db_trip, field, value)

        db.commit()
        db.refresh(db_trip)
        return db_trip

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    db_trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not db_trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    if db_trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    db.delete(db_trip)
    db.commit()
    return None
