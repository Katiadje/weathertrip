# 🌍 WeatherTrip

Application web de gestion de voyages intégrant les données météo en temps réel.

## 📋 Description

WeatherTrip est une application full-stack permettant de :
- Gérer ses voyages (création, consultation, modification, suppression)
- Ajouter des destinations à chaque voyage
- Consulter la météo actuelle et les prévisions pour chaque destination
- Visualiser des statistiques sur ses voyages avec Chart.js
- Authentification simple des utilisateurs

## 🛠️ Stack Technique

### Backend
- **Python 3.10+**
- **FastAPI** - Framework web moderne et performant
- **SQLAlchemy** - ORM pour la gestion de la base de données
- **PostgreSQL** - Base de données relationnelle
- **OpenWeatherMap API** - API météo gratuite
- **JWT** - Authentification par tokens

### Frontend
- **HTML5 / CSS3** - Interface responsive
- **JavaScript Vanilla** - Logique client sans framework
- **Chart.js** - Visualisation des statistiques

## 📁 Structure du Projet

```
weathertrip/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   │   └── database.py           # Configuration DB
│   │   ├── models/
│   │   │   ├── models.py             # Modèles SQLAlchemy
│   │   │   └── schemas.py            # Schémas Pydantic
│   │   ├── routes/
│   │   │   ├── users.py              # Routes utilisateurs
│   │   │   ├── trips.py              # Routes voyages
│   │   │   ├── destinations.py       # Routes destinations
│   │   │   └── weather.py            # Routes météo
│   │   ├── services/
│   │   │   ├── auth_service.py       # Service d'authentification
│   │   │   └── weather_service.py    # Service météo
│   │   └── main.py                   # Application principale
│   ├── requirements.txt              # Dépendances Python
│   └── .env.example                  # Variables d'environnement
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css             # Styles CSS
│   │   └── js/
│   │       └── app.js                # Logique JavaScript
│   └── templates/
│       └── index.html                # Page principale
├── docs/
│   ├── database_schema_dbdiagram.txt # Schéma pour dbdiagram.io
│   └── database_schema_mocodo.txt    # Schéma pour Mocodo
└── README.md
```

## 🚀 Installation

### Prérequis
- Python 3.10 ou supérieur
- PostgreSQL 12 ou supérieur
- Clé API OpenWeatherMap (gratuite)

### 1. Cloner le projet
```bash
git clone <url-du-repo>
cd weathertrip
```

### 2. Configurer la base de données

#### Avec PostgreSQL
```bash
# Créer la base de données
createdb weathertrip_db

# Ou avec psql
psql -U postgres
CREATE DATABASE weathertrip_db;
```

### 3. Backend

```bash
cd backend

# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur Windows:
venv\Scripts\activate
# Sur Linux/Mac:
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer le fichier .env avec vos paramètres
```

### 4. Configuration de l'API Météo

1. Créer un compte gratuit sur https://openweathermap.org/api
2. Obtenir votre clé API
3. Ajouter la clé dans le fichier `.env` :
```
OPENWEATHER_API_KEY=votre_cle_api_ici
```

### 5. Lancer l'application

```bash
# Depuis le dossier backend/
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'application sera accessible sur : http://localhost:8000

## 📊 Schémas de Base de Données

### Pour dbdiagram.io
Copier le contenu de `docs/database_schema_dbdiagram.txt` sur https://dbdiagram.io/

### Pour Mocodo
Copier le contenu de `docs/database_schema_mocodo.txt` dans Mocodo en ligne ou local.

## 🎯 Utilisation

### 1. Inscription / Connexion
- S'inscrire avec un nom d'utilisateur, email et mot de passe
- Se connecter avec ses identifiants

### 2. Créer un voyage
- Renseigner le nom du voyage
- Ajouter des dates (optionnel)
- Ajouter une description (optionnel)

### 3. Ajouter des destinations
- Cliquer sur "+ Destination" sur un voyage
- Renseigner la ville et le pays
- Ajouter des dates d'arrivée et de départ (optionnel)

### 4. Consulter la météo
- Cliquer sur l'icône météo 🌤️ pour une destination
- Ou voir la météo de toutes les destinations d'un voyage

### 5. Visualiser les statistiques
- Un graphique Chart.js affiche le nombre de destinations par voyage

## 🔧 Fonctionnalités

### Obligatoires ✅
- [x] Backend Python avec FastAPI
- [x] Base de données PostgreSQL
- [x] Frontend web HTML/CSS/JS
- [x] Gestion des utilisateurs
- [x] CRUD voyages
- [x] CRUD destinations
- [x] Intégration API météo OpenWeatherMap
- [x] Affichage de la météo
- [x] Stockage en base de données
- [x] Graphiques avec Chart.js

### Bonus (Optionnels) 🎁
- [x] Cache des données météo
- [x] Prévisions météo
- [ ] Export PDF du voyage
- [ ] Carte interactive des destinations
- [ ] Recommandation de dates selon la météo

## 📡 API Endpoints

### Utilisateurs
- `POST /users/register` - Inscription
- `POST /users/login` - Connexion
- `GET /users/me` - Profil utilisateur

### Voyages
- `POST /trips/` - Créer un voyage
- `GET /trips/` - Liste des voyages
- `GET /trips/{id}` - Détail d'un voyage
- `PUT /trips/{id}` - Modifier un voyage
- `DELETE /trips/{id}` - Supprimer un voyage

### Destinations
- `POST /destinations/` - Ajouter une destination
- `GET /destinations/trip/{trip_id}` - Destinations d'un voyage
- `GET /destinations/{id}` - Détail d'une destination
- `PUT /destinations/{id}` - Modifier une destination
- `DELETE /destinations/{id}` - Supprimer une destination

### Météo
- `GET /weather/destination/{id}` - Météo d'une destination
- `POST /weather/destination/{id}/forecast` - Récupérer les prévisions
- `GET /weather/trip/{id}` - Météo de toutes les destinations
- `GET /weather/city/{city}` - Rechercher la météo d'une ville

## 🧪 Tests

```bash
# Installer pytest (déjà dans requirements.txt)
pip install pytest pytest-asyncio

# Lancer les tests
pytest
```

## 📝 Notes Importantes

⚠️ **API Météo Gratuite**
- Limité à 60 appels/minute
- Données mises en cache pour 1 heure
- Prévisions sur 5 jours (par tranche de 3h)

⚠️ **Production**
- Changer `SECRET_KEY` dans `auth_service.py`
- Configurer CORS correctement dans `main.py`
- Utiliser HTTPS
- Sécuriser les variables d'environnement

## 🤝 Contribution

Ce projet a été réalisé dans le cadre du projet M2-web.

### Répartition des tâches (suggérée)
- **Étudiant 1** : Backend Python, API météo, Base de données
- **Étudiant 2** : Frontend web, Intégration données météo, UX/UI

## 📄 Livrables

- [x] Code source du projet
- [x] Application fonctionnelle
- [x] Base de données configurée
- [x] Documentation d'installation et d'utilisation
- [ ] Démonstration finale

## 🎓 Critères d'Évaluation

| Critère | Pondération |
|---------|-------------|
| Back-end Python | 30 % |
| Base de données | 20 % |
| Front-end | 20 % |
| Intégration API météo | 15 % |
| Qualité du code & documentation | 15 % |

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

## 📧 Support

Pour toute question, consulter la documentation ou contacter l'équipe projet.

---

Fait avec ❤️ pour le projet M2-web
