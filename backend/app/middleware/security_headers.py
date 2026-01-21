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

        # 1) MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 2) Clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # 3) XSS Protection (legacy)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 4) CSP
        # En dev: autoriser Chart.js CDN + Swagger UI
        # En prod: garder strict mais on autorise toujours jsdelivr si tu utilises le CDN
        csp_directives = [
            "default-src 'self'",
            "base-uri 'self'",
            "frame-ancestors 'none'",

            # Scripts: self + inline (Swagger en a besoin) + jsdelivr (Chart.js)
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",

            # Styles: Swagger utilise inline
            "style-src 'self' 'unsafe-inline'",

            # Images
            "img-src 'self' data: https:",

            # Fonts
            "font-src 'self' data:",

            # ✅ FIX: autoriser jsdelivr aussi en connect-src (sinon erreur console)
            "connect-src 'self' https://cdn.jsdelivr.net",

            # (optionnel) si tu utilises des workers un jour
            "worker-src 'self' blob:",
        ]
        response.headers["Content-Security-Policy"] = "; ".join(csp_directives)

        # 5) HSTS (prod only)
        if self.is_production:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        # 6) Permissions Policy
        permissions = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
        ]
        response.headers["Permissions-Policy"] = ", ".join(permissions)

        # 7) Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 8) Cache-Control sur endpoints sensibles
        if request.url.path.startswith("/users") or request.url.path.startswith("/trips"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

        return response


def setup_security_headers(app, environment: str = None):
    app.add_middleware(SecurityHeadersMiddleware, environment=environment)
    print(f"✅ Security Headers enabled (environment: {environment or 'development'})")
