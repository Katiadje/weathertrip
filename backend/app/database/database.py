from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Charger les variables d'environnement
load_dotenv()

# Mode test : utiliser SQLite
if os.getenv("TESTING") == "true":
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # ✅ MODIFIÉ : Fallback vers MySQL local si DATABASE_URL n'est pas définie
    SQLALCHEMY_DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://weathertrip_user:weathertrip_pass@localhost:3306/weathertrip_db"
    )
    
    # Vérification
    if not SQLALCHEMY_DATABASE_URL:
        raise ValueError("DATABASE_URL n'est pas défini")
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session locale
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

# Dépendance pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()