import os
os.environ["TESTING"] = "false"

from app.database.database import Base, engine
from app.models import models

print("🔄 Suppression des anciennes tables...")
Base.metadata.drop_all(bind=engine)

print("🔄 Création des tables avec contraintes de sécurité...")
Base.metadata.create_all(bind=engine)

print("✅ Tables créées avec succès avec toutes les contraintes de sécurité !")
print("\nContraintes appliquées :")
print("  - Username: min 3 caractères, pas d'espaces vides")
print("  - Email: min 5 caractères")
print("  - Trip name: min 3 caractères")
print("  - City/Country: min 2 caractères")
print("  - Latitude: -90 à 90")
print("  - Longitude: -180 à 180")
print("  - Humidity/Clouds: 0 à 100")