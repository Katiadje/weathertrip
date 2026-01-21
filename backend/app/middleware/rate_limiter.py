"""
Middleware de rate limiting (limitation du nombre de requêtes)
Protège contre les attaques par brute force et DDoS
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from typing import Callable

def get_remote_address_or_default(request: Request) -> str:
    """
    Récupère l'adresse IP du client
    Gère les cas où l'IP n'est pas disponible
    """
    if request.client:
        return request.client.host
    return "127.0.0.1"

# Créer le limiter global
limiter = Limiter(
    key_func=get_remote_address_or_default,
    default_limits=["200/hour"],  # Limite globale: 200 requêtes/heure par IP
    storage_uri="memory://",  # En production, utiliser Redis
)

def setup_rate_limiting(app):
    """
    Configure le rate limiting sur l'application
    
    Usage dans main.py:
        from app.middleware import setup_rate_limiting, limiter
        setup_rate_limiting(app)
    
    Puis dans vos routes:
        @app.post("/users/register")
        @limiter.limit("5/minute")
        async def register(request: Request, ...):
            ...
    """
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    print("✅ Rate Limiting enabled (200 req/hour global)")


# Décorateurs prédéfinis pour les cas courants
def strict_rate_limit(func: Callable) -> Callable:
    """Limite stricte : 5 requêtes/minute (pour login, register)"""
    return limiter.limit("5/minute")(func)

def medium_rate_limit(func: Callable) -> Callable:
    """Limite moyenne : 30 requêtes/minute (pour les API normales)"""
    return limiter.limit("30/minute")(func)

def relaxed_rate_limit(func: Callable) -> Callable:
    """Limite relâchée : 100 requêtes/minute (pour les GET)"""
    return limiter.limit("100/minute")(func)


# Exemple d'utilisation dans les routes:
"""
from app.middleware.rate_limiter import limiter, strict_rate_limit

@router.post("/users/register")
@limiter.limit("5/minute")  # Max 5 inscriptions par minute par IP
async def register(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    ...

@router.post("/users/login")
@strict_rate_limit  # Utiliser le décorateur prédéfini
async def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    ...

@router.get("/trips")
@limiter.limit("60/minute")  # Plus permissif pour les GET
async def get_trips(request: Request, user_id: int, db: Session = Depends(get_db)):
    ...
"""