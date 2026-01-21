from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from pydantic import ValidationError

from ..database.database import get_db
from ..models import models, schemas
from ..services import auth_service

router = APIRouter(prefix="/destinations", tags=["destinations"])

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


@router.post("/", response_model=schemas.Destination, status_code=status.HTTP_201_CREATED)
def create_destination(
    destination: schemas.DestinationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Ajoute une destination à un voyage de l'utilisateur connecté.
    ✅ trip_id est lu depuis le body (destination.trip_id) pour matcher les tests.
    """
    try:
        # Vérifier que le voyage existe
        trip = db.query(models.Trip).filter(models.Trip.id == destination.trip_id).first()
        if not trip:
            raise HTTPException(status_code=404, detail="Voyage non trouvé")

        # 🔒 AuthZ: le voyage doit appartenir au user connecté
        if trip.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit")

        # Créer la destination avec nettoyage
        db_destination = models.Destination(
            city=destination.city.strip(),
            country=destination.country.strip(),
            arrival_date=destination.arrival_date,
            departure_date=destination.departure_date,
            latitude=destination.latitude,
            longitude=destination.longitude,
            trip_id=destination.trip_id,
        )

        db.add(db_destination)
        db.commit()
        db.refresh(db_destination)
        return db_destination

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la création de la destination")


@router.get("/trip/{trip_id}", response_model=List[schemas.Destination])
def get_destinations_by_trip(
    trip_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Récupère toutes les destinations d'un voyage
    🔒 seulement si le voyage appartient au user connecté
    """
    trip = db.query(models.Trip).filter(models.Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Voyage non trouvé")
    if trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    destinations = db.query(models.Destination).filter(models.Destination.trip_id == trip_id).all()
    return destinations


@router.get("/{destination_id}", response_model=schemas.Destination)
def get_destination(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Récupère une destination par ID
    🔒 seulement si elle appartient à un voyage du user connecté
    """
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if not destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")

    trip = db.query(models.Trip).filter(models.Trip.id == destination.trip_id).first()
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    return destination


@router.put("/{destination_id}", response_model=schemas.Destination)
def update_destination(
    destination_id: int,
    destination_update: schemas.DestinationUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Met à jour une destination
    🔒 seulement si elle appartient au user connecté
    """
    try:
        db_destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
        if not db_destination:
            raise HTTPException(status_code=404, detail="Destination non trouvée")

        trip = db.query(models.Trip).filter(models.Trip.id == db_destination.trip_id).first()
        if not trip or trip.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Accès interdit")

        update_data = destination_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            if field in ["city", "country"] and value is not None:
                value = value.strip()
                if not value:
                    raise HTTPException(
                        status_code=422,
                        detail=f"{field.capitalize()} ne peut pas être vide"
                    )
            setattr(db_destination, field, value)

        db.commit()
        db.refresh(db_destination)
        return db_destination

    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour")


@router.delete("/{destination_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_destination(
    destination_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Supprime une destination
    🔒 seulement si elle appartient au user connecté
    """
    db_destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if not db_destination:
        raise HTTPException(status_code=404, detail="Destination non trouvée")

    trip = db.query(models.Trip).filter(models.Trip.id == db_destination.trip_id).first()
    if not trip or trip.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Accès interdit")

    db.delete(db_destination)
    db.commit()
    return None
