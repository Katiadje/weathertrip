"""
Middleware de protection CSRF (Cross-Site Request Forgery)
Protège contre les attaques où un site malveillant fait des requêtes à votre API
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import secrets
import hmac
from typing import Callable
import os

class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui génère et valide des tokens CSRF
    """
    
    def __init__(self, app, secret_key: str = None):
        super().__init__(app)
        self.secret_key = secret_key or os.getenv("SECRET_KEY", "fallback-secret-change-me")
        self.safe_methods = {"GET", "HEAD", "OPTIONS"}
        self.excluded_paths = {
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
        }
        # Mode strict : en développement False, en production True
        self.strict_mode = os.getenv("ENVIRONMENT", "development") == "production"
    
    def _is_excluded_path(self, path: str) -> bool:
        """Vérifie si le chemin est exclu de la vérification CSRF"""
        return any(path.startswith(excluded) for excluded in self.excluded_paths)
    
    def generate_csrf_token(self, request: Request) -> str:
        """Génère un token CSRF sécurisé lié à la session"""
        # Générer un token aléatoire
        random_token = secrets.token_urlsafe(32)
        
        # Créer un HMAC pour lier le token à la session/IP
        remote_addr = request.client.host if request.client else "unknown"
        message = f"{random_token}:{remote_addr}".encode()
        signature = hmac.new(
            self.secret_key.encode(),
            message,
            digestmod="sha256"
        ).hexdigest()
        
        # Token final = random_token + signature
        return f"{random_token}.{signature}"
    
    def validate_csrf_token(self, token: str, request: Request) -> bool:
        """Valide un token CSRF"""
        if not token:
            return False
        
        try:
            # Séparer le token et la signature
            parts = token.split(".")
            if len(parts) != 2:
                return False
            
            random_token, provided_signature = parts
            
            # Recréer la signature attendue
            remote_addr = request.client.host if request.client else "unknown"
            message = f"{random_token}:{remote_addr}".encode()
            expected_signature = hmac.new(
                self.secret_key.encode(),
                message,
                digestmod="sha256"
            ).hexdigest()
            
            # Comparaison sécurisée contre les timing attacks
            return hmac.compare_digest(provided_signature, expected_signature)
        
        except Exception:
            return False
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Exclure certains chemins (docs, health check, etc.)
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Les méthodes GET, HEAD, OPTIONS sont considérées comme sûres
        if request.method in self.safe_methods:
            response = await call_next(request)
            # Ajouter un token CSRF pour les futures requêtes POST/PUT/DELETE
            csrf_token = self.generate_csrf_token(request)
            response.headers["X-CSRF-Token"] = csrf_token
            return response
        
        # Pour POST, PUT, DELETE, PATCH : vérifier le token CSRF
        csrf_token = request.headers.get("X-CSRF-Token")
        
        if not csrf_token:
            if self.strict_mode:
                raise HTTPException(
                    status_code=403,
                    detail="CSRF token missing. Include X-CSRF-Token header."
                )
            else:
                # En développement, juste un warning dans les logs
                print("⚠️  WARNING: CSRF token missing (development mode)")
        
        elif not self.validate_csrf_token(csrf_token, request):
            if self.strict_mode:
                raise HTTPException(
                    status_code=403,
                    detail="Invalid CSRF token."
                )
            else:
                print("⚠️  WARNING: Invalid CSRF token (development mode)")
        
        # Traiter la requête
        response = await call_next(request)
        
        # Générer un nouveau token pour la prochaine requête
        new_csrf_token = self.generate_csrf_token(request)
        response.headers["X-CSRF-Token"] = new_csrf_token
        
        return response


def setup_csrf_protection(app, secret_key: str = None):
    """
    Configure la protection CSRF sur l'application
    
    Usage dans main.py:
        from app.middleware import setup_csrf_protection
        setup_csrf_protection(app, secret_key="your-secret-key")
    """
    app.add_middleware(CSRFProtectionMiddleware, secret_key=secret_key)
    print("✅ CSRF Protection enabled")