# 🌍 WeatherTrip

Application web de gestion de voyages avec météo en temps réel et **sécurité renforcée**.

## 📋 Description

WeatherTrip permet de :
- ✈️ Gérer ses voyages (CRUD complet)
- 📍 Ajouter des destinations à chaque voyage
- 🌤️ Consulter la météo actuelle et prévisions (cache 1h)
- 📊 Visualiser des statistiques avec Chart.js
- 🔐 S'authentifier de manière sécurisée (JWT + Bcrypt)

---

## 🛠️ Stack Technique

**Backend** : Python 3.10+, FastAPI, SQLAlchemy, PostgreSQL/MySQL, JWT, Bcrypt, SlowAPI  
**Frontend** : HTML5/CSS3, JavaScript ES6 Modules, Chart.js  
**Sécurité** : CSRF Protection, Rate Limiting, Brute Force Protection, Security Headers, Input Validation  
**Tests** : pytest, pytest-asyncio, unittest.mock

---

## 🔒 Sécurité Implémentée

### Middlewares
- **Security Headers** : CSP, X-Frame-Options, HSTS, X-Content-Type-Options, etc.
- **CSRF Protection** : Tokens HMAC SHA-256 avec liaison IP
- **Rate Limiting** : 200 req/h global, 5 req/min sur login/register
- **Brute Force** : 5 tentatives max, blocage 15 min

### Validation Multi-Niveaux
- **Pydantic** : Validation stricte des inputs (regex, length, format)
- **SQL Injection** : Détection patterns malveillants + contraintes DB
- **Database** : CHECK constraints sur tous les champs critiques

### Authentification
- **JWT** : Tokens avec expiration (30 min)
- **Bcrypt** : Hash adaptatif des mots de passe
- **Authorization** : Isolation des données par utilisateur (user_id)

### Règles de Validation
- Username : 3-50 chars, alphanumérique + `_-`
- Email : Format EmailStr validé
- Password : 8+ chars, 1 majuscule, 1 minuscule, 1 chiffre
- Villes/Pays : Lettres, espaces, tirets, apostrophes uniquement

---

## 📁 Structure

```
weathertrip/
├── backend/
│   ├── app/
│   │   ├── database/          # Configuration SQLAlchemy
│   │   ├── models/            # ORM + Pydantic schemas
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic (auth, weather)
│   │   ├── middleware/        # Security (CSRF, headers, rate limit, brute force)
│   │   └── main.py
│   ├── tests/                 # pytest tests
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── static/
    │   ├── css/style.css
    │   └── js/               # ES6 modules (auth, trips, weather, etc.)
    └── templates/index.html
```

---

## 🚀 Installation

### 1. Prérequis
- Python 3.10+
- PostgreSQL 12+ ou MySQL 8+
- Clé API OpenWeatherMap (gratuite sur https://openweathermap.org/api)

### 2. Setup

```bash
# Clone
git clone <url-du-repo>
cd weathertrip

# Base de données
createdb weathertrip_db  # PostgreSQL
# OU
mysql -u root -p -e "CREATE DATABASE weathertrip_db;"

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configuration .env
cp .env.example .env
# Éditer .env avec vos paramètres
```

### 3. Configuration `.env`

```env
DATABASE_URL=postgresql://user:password@localhost:5432/weathertrip_db
SECRET_KEY=<générer-avec-secrets.token_urlsafe(32)>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENWEATHER_API_KEY=<votre-clé-api>
ENVIRONMENT=development
```

**Générer SECRET_KEY** :
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Initialiser DB

```bash
python -c "from app.database.database import engine; from app.models.models import Base; Base.metadata.create_all(bind=engine)"
```

### 5. Lancer

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Accès** : http://localhost:8000  
**Docs API** : http://localhost:8000/docs

---

## 📡 API Endpoints

### Authentification
- `POST /users/register` - Inscription (rate limit: 5/min)
- `POST /users/login` - Connexion JWT (rate limit: 5/min + brute force)
- `GET /users/me` - Profil utilisateur (auth requise)

### Voyages (Auth JWT requise)
- `POST /trips/` - Créer voyage
- `GET /trips/` - Liste voyages (pagination)
- `GET /trips/{id}` - Détail voyage
- `PUT /trips/{id}` - Modifier voyage
- `DELETE /trips/{id}` - Supprimer voyage

### Destinations (Auth JWT requise)
- `POST /destinations/` - Ajouter destination
- `GET /destinations/trip/{trip_id}` - Destinations d'un voyage
- `GET /destinations/{id}` - Détail destination
- `PUT /destinations/{id}` - Modifier
- `DELETE /destinations/{id}` - Supprimer

### Météo
- `GET /weather/destination/{id}` - Météo destination (cache 1h)
- `POST /weather/destination/{id}/forecast` - Récupérer prévisions
- `GET /weather/trip/{id}` - Météo toutes destinations
- `GET /weather/city/{city}` - Rechercher météo ville

**Exemple** :
```bash
# Register
curl -X POST "http://localhost:8000/users/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"SecurePass123"}'

# Login
curl -X POST "http://localhost:8000/users/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123"}'

# Create Trip (avec token)
curl -X POST "http://localhost:8000/trips/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Vacances été","description":"Tour de France"}'
```

---

## 🧪 Tests

```bash
# Installation
pip install pytest pytest-asyncio httpx

# Lancer tous les tests
pytest

# Avec verbose
pytest -v

# Avec coverage
pytest --cov=app --cov-report=html
```

**Tests disponibles** :
- `test_users_routes.py` - API utilisateurs
- `test_trips_routes.py` - API voyages
- `test_destinations_routes.py` - API destinations
- `test_weather_routes.py` - API météo (avec mocking)
- `test_auth_service.py` - Service authentification
- `test_weather_service.py` - Service météo

---

## 🎯 Utilisation

1. **S'inscrire** : Username (3-50 chars), Email valide, Password (8+ chars, 1 maj, 1 min, 1 chiffre)
2. **Se connecter** : Récupérer token JWT valide 30 min
3. **Créer voyage** : Nom (obligatoire), dates (optionnel), description (optionnel)
4. **Ajouter destinations** : Ville, pays (lettres uniquement), dates (optionnel)
5. **Consulter météo** : Cliquer icône 🌤️ sur destination
6. **Voir stats** : Graphique Chart.js automatique

---

## ⚠️ Notes Importantes

### API Météo
- **Limite** : 60 appels/minute (gratuit)
- **Cache** : Données mise en cache 1 heure
- **Prévisions** : 5 jours par tranches de 3h

### Production Checklist
- [ ] Générer SECRET_KEY forte (32+ chars)
- [ ] ENVIRONMENT=production
- [ ] Activer HTTPS (obligatoire)
- [ ] Configurer CORS (origins spécifiques)
- [ ] Utiliser Redis pour rate limiting
- [ ] Activer logs et monitoring
- [ ] Sauvegardes DB automatiques
- [ ] Configurer firewall

**CORS Production** (main.py) :
```python
origins = ["https://votre-domaine.com"]  # Pas ["*"] !
```

**Redis Rate Limiting** :
```python
storage_uri="redis://localhost:6379"  # Au lieu de memory://
```

---

## 🏆 Fonctionnalités

### Obligatoires ✅
- [x] Backend Python FastAPI
- [x] Base de données PostgreSQL/MySQL
- [x] Frontend HTML/CSS/JS
- [x] Authentification JWT
- [x] CRUD voyages + destinations
- [x] API météo OpenWeatherMap
- [x] Cache météo 1h
- [x] Graphiques Chart.js

### Sécurité ✅
- [x] JWT + Bcrypt
- [x] Brute Force Protection (5/15min)
- [x] Rate Limiting (200/h)
- [x] Security Headers (CSP, HSTS, etc.)
- [x] CSRF Protection
- [x] Input Validation (Pydantic + Regex)
- [x] SQL Injection Prevention
- [x] Authorization par user

### Bonus ✅
- [x] Tests pytest
- [x] Architecture modulaire ES6
- [x] Prévisions météo 5 jours
- [x] Contraintes DB
- [x] Documentation API auto
- [x] Normalisation codes pays

---

## 🐛 Dépannage

**"SECRET_KEY non défini"** :
```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
```

**Erreur DB** :
```bash
# Vérifier DB existe
psql -l | grep weathertrip_db

# Vérifier .env
cat .env | grep DATABASE_URL
```

**IP bloquée (brute force)** : Attendre 15 min ou redémarrer app

**Rate limit exceeded** : Attendre expiration ou redémarrer app

---

## 📚 Ressources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Chart.js](https://www.chartjs.org/docs/)

---

## 📄 License

MIT License - Projet M2-web

---

**Fait avec ❤️ et 🔒**