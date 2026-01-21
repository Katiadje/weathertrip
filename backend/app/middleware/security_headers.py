"""
Middleware qui ajoute des headers de sécurité HTTP
Protège contre XSS, Clickjacking, MIME sniffing, etc.
"""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import Callable
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Ajoute automatiquement des headers de sécurité à toutes les réponses
    """
    
    def __init__(self, app, environment: str = "development"):
        super().__init__(app)
        self.environment = environment or os.getenv("ENVIRONMENT", "development")
        self.is_production = self.environment == "production"
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # 1. Protection contre le MIME type sniffing
        # Empêche le navigateur de deviner le type de contenu
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 2. Protection contre le Clickjacking
        # Empêche ton site d'être chargé dans une iframe
        response.headers["X-Frame-Options"] = "DENY"
        
        # 3. Protection XSS (ancienne méthode, mais toujours utile)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 4. Content Security Policy (CSP)
        # Définit quelles ressources peuvent être chargées
        csp_directives = [
            "default-src 'self'",  # Par défaut, uniquement les ressources du même domaine
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",  # Scripts autorisés (Chart.js)
            "style-src 'self' 'unsafe-inline'",  # Styles inline autorisés
            "img-src 'self' data: https:",  # Images depuis le même domaine, data URIs, et HTTPS
            "font-src 'self' data:",  # Polices
            "connect-src 'self'",  # Connexions AJAX uniquement vers le même domaine
            "frame-ancestors 'none'",  # Pas d'iframe (similaire à X-Frame-Options)
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)
        
        # 5. HSTS (HTTP Strict Transport Security)
        # Force HTTPS (uniquement en production)
        if self.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        
        # 6. Permissions Policy (anciennement Feature Policy)
        # Désactive les APIs dangereuses
        permissions = [
            "geolocation=()",  # Pas de géolocalisation
            "microphone=()",   # Pas de microphone
            "camera=()",       # Pas de caméra
            "payment=()",      # Pas de paiement
            "usb=()",         # Pas d'USB
            "magnetometer=()", # Pas de magnétomètre
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)
        
        # 7. Referrer Policy
        # Contrôle les informations de référence envoyées
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 8. Cache Control pour les données sensibles
        # Empêche la mise en cache des pages authentifiées
        if request.url.path.startswith("/users") or request.url.path.startswith("/trips"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        return response


def setup_security_headers(app, environment: str = None):
    """
    Configure les headers de sécurité sur l'application
    
    Usage dans main.py:
        from app.middleware import setup_security_headers
        setup_security_headers(app, environment="production")
    """
    app.add_middleware(SecurityHeadersMiddleware, environment=environment)
    print(f"✅ Security Headers enabled (environment: {environment or 'development'})")