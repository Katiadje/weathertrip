from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import ValidationError

from ..database.database import get_db
from ..models import models, schemas
from ..services import auth_service

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur avec validation stricte
    """
    try:
        # Vérifier si l'utilisateur existe déjà
        db_user = db.query(models.User).filter(models.User.username == user.username.strip()).first()
        if db_user:
            raise HTTPException(
                status_code=400, 
                detail="Nom d'utilisateur déjà utilisé"
            )
        
        db_user = db.query(models.User).filter(models.User.email == user.email.lower()).first()
        if db_user:
            raise HTTPException(
                status_code=400, 
                detail="Email déjà utilisé"
            )
        
        # Créer le nouvel utilisateur avec validation
        hashed_password = auth_service.get_password_hash(user.password)
        db_user = models.User(
            username=user.username.strip(),
            email=user.email.lower(),
            password_hash=hashed_password
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de l'inscription")

@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur avec validation
    """
    try:
        user = auth_service.authenticate_user(
            db, 
            user_credentials.username.strip(), 
            user_credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identifiants incorrects",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Créer le token d'accès
        access_token_expires = timedelta(minutes=auth_service.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = auth_service.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username
        }
        
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/me", response_model=schemas.User)
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Récupère l'utilisateur connecté
    """
    user = auth_service.get_current_user_from_token(token, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user