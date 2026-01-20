# 🚀 Guide d'Installation Rapide - WeatherTrip

## Option 1 : Installation avec Docker (Recommandé)

### Prérequis
- Docker et Docker Compose installés

### Étapes
1. **Obtenir une clé API OpenWeatherMap**
   - Aller sur https://openweathermap.org/api
   - Créer un compte gratuit
   - Obtenir votre clé API

2. **Configurer les variables d'environnement**
   ```bash
   # Créer un fichier .env à la racine
   echo "OPENWEATHER_API_KEY=votre_cle_api" > .env
   ```

3. **Lancer l'application**
   ```bash
   docker-compose up -d
   ```

4. **Accéder à l'application**
   - Frontend: http://localhost:8000
   - API Docs: http://localhost:8000/docs

5. **Se connecter avec le compte de test**
   - Username: `demo`
   - Password: `demo123`

### Commandes utiles
```bash
# Voir les logs
docker-compose logs -f

# Arrêter l'application
docker-compose down

# Arrêter et supprimer les volumes
docker-compose down -v
```

---

## Option 2 : Installation Manuelle

### Prérequis
- Python 3.10+
- PostgreSQL 12+

### 1. Configuration PostgreSQL
```bash
# Créer la base de données
createdb weathertrip_db

# Importer le schéma
psql -d weathertrip_db -f docs/init_database.sql
```

### 2. Backend
```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer .env
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 3. Lancer l'application
```bash
# Depuis le dossier backend/
uvicorn app.main:app --reload
```

### 4. Accéder à l'application
- Frontend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🔑 Obtenir une Clé API OpenWeatherMap

1. Aller sur https://openweathermap.org/api
2. Cliquer sur "Get API Key" ou "Sign Up"
3. Créer un compte gratuit
4. Dans votre profil, section "API keys", copier votre clé
5. Ajouter la clé dans le fichier `.env`

**Plan Gratuit:**
- 60 appels/minute
- 1,000,000 appels/mois
- Données actuelles + prévisions 5 jours
- Parfait pour ce projet !

---

## 🧪 Tester l'API

### Avec curl
```bash
# Health check
curl http://localhost:8000/health

# Créer un utilisateur
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@test.com","password":"test123"}'

# Se connecter
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test123"}'
```

### Avec l'interface Swagger
Aller sur http://localhost:8000/docs

---

## 📊 Visualiser le Schéma de Base de Données

### Avec dbdiagram.io
1. Aller sur https://dbdiagram.io/
2. Copier le contenu de `docs/database_schema_dbdiagram.txt`
3. Coller dans l'éditeur

### Avec Mocodo
1. Aller sur http://mocodo.wingi.net/
2. Copier le contenu de `docs/database_schema_mocodo.txt`
3. Coller et cliquer sur "Générer"

---

## ❓ Problèmes Courants

### Erreur : "Connection refused" sur la base de données
- Vérifier que PostgreSQL est bien lancé
- Vérifier l'URL de connexion dans `.env`
- Avec Docker : attendre que le conteneur DB soit prêt

### Erreur : "Module not found"
- Vérifier que l'environnement virtuel est activé
- Réinstaller les dépendances : `pip install -r requirements.txt`

### Erreur API météo : "Invalid API key"
- Vérifier que la clé API est correcte dans `.env`
- Attendre quelques minutes après la création de la clé (activation)

### Le frontend ne se charge pas
- Vérifier que le backend est bien lancé
- Vérifier l'URL dans `frontend/static/js/app.js` (doit être http://localhost:8000)

---

## 📚 Ressources

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation OpenWeatherMap](https://openweathermap.org/api)
- [Guide PostgreSQL](https://www.postgresql.org/docs/)

---

## 🎯 Prochaines Étapes

1. Créer votre premier voyage
2. Ajouter des destinations
3. Consulter la météo
4. Visualiser vos statistiques
5. (Bonus) Exporter en PDF

Bon voyage avec WeatherTrip ! 🌍✈️
