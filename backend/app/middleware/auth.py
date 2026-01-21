"""
Middleware et utilitaires pour renforcer la sécurité de l'authentification
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Optional
from datetime import datetime, timedelta
import time

class LoginAttemptTracker:
    """
    Suit les tentatives de connexion échouées par IP
    Bloque temporairement après trop de tentatives (protection brute force)
    """
    
    def __init__(self, max_attempts: int = 5, block_duration: int = 900):
        """
        Args:
            max_attempts: Nombre maximum de tentatives avant blocage (défaut: 5)
            block_duration: Durée du blocage en secondes (défaut: 900 = 15 min)
        """
        self.max_attempts = max_attempts
        self.block_duration = block_duration
        self.attempts: Dict[str, list] = {}  # IP -> liste de timestamps
        self.blocked: Dict[str, float] = {}  # IP -> timestamp de déblocage
    
    def is_blocked(self, ip: str) -> bool:
        """Vérifie si une IP est bloquée"""
        if ip in self.blocked:
            if time.time() < self.blocked[ip]:
                return True
            else:
                # Le blocage est expiré, nettoyer
                del self.blocked[ip]
                if ip in self.attempts:
                    del self.attempts[ip]
        return False
    
    def record_failed_attempt(self, ip: str) -> None:
        """Enregistre une tentative échouée"""
        now = time.time()
        
        # Initialiser si nécessaire
        if ip not in self.attempts:
            self.attempts[ip] = []
        
        # Ajouter la tentative
        self.attempts[ip].append(now)
        
        # Nettoyer les anciennes tentatives (> 1 heure)
        self.attempts[ip] = [
            t for t in self.attempts[ip]
            if now - t < 3600  # Garder seulement les tentatives de la dernière heure
        ]
        
        # Bloquer si trop de tentatives
        if len(self.attempts[ip]) >= self.max_attempts:
            self.blocked[ip] = now + self.block_duration
            print(f"🚫 IP {ip} blocked for {self.block_duration}s after {self.max_attempts} failed attempts")
    
    def record_successful_attempt(self, ip: str) -> None:
        """Réinitialise le compteur après une connexion réussie"""
        if ip in self.attempts:
            del self.attempts[ip]
        if ip in self.blocked:
            del self.blocked[ip]
    
    def get_remaining_attempts(self, ip: str) -> int:
        """Retourne le nombre de tentatives restantes"""
        if ip not in self.attempts:
            return self.max_attempts
        return max(0, self.max_attempts - len(self.attempts[ip]))
    
    def get_block_time_remaining(self, ip: str) -> Optional[int]:
        """Retourne le temps restant de blocage en secondes"""
        if ip in self.blocked:
            remaining = int(self.blocked[ip] - time.time())
            return max(0, remaining)
        return None


# Instance globale du tracker
login_tracker = LoginAttemptTracker(max_attempts=5, block_duration=900)


class BruteForceProtectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware qui protège contre les attaques brute force sur le login
    """
    
    def __init__(self, app, login_endpoints: list = None):
        super().__init__(app)
        self.login_endpoints = login_endpoints or ["/users/login"]
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Vérifier uniquement les endpoints de login
        if not any(request.url.path.endswith(endpoint) for endpoint in self.login_endpoints):
            return await call_next(request)
        
        # Récupérer l'IP
        ip = request.client.host if request.client else "unknown"
        
        # Vérifier si l'IP est bloquée
        if login_tracker.is_blocked(ip):
            remaining = login_tracker.get_block_time_remaining(ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many failed login attempts. Try again in {remaining} seconds."
            )
        
        # Continuer avec la requête
        response = await call_next(request)
        
        # Si échec (401), enregistrer
        if response.status_code == 401:
            login_tracker.record_failed_attempt(ip)
            remaining = login_tracker.get_remaining_attempts(ip)
            if remaining > 0:
                response.headers["X-Remaining-Attempts"] = str(remaining)
        
        # Si succès (200), réinitialiser
        elif response.status_code == 200:
            login_tracker.record_successful_attempt(ip)
        
        return response


def setup_brute_force_protection(app, login_endpoints: list = None):
    """
    Configure la protection anti-brute force
    
    Usage dans main.py:
        from app.middleware.auth import setup_brute_force_protection
        setup_brute_force_protection(app, login_endpoints=["/users/login"])
    """
    app.add_middleware(BruteForceProtectionMiddleware, login_endpoints=login_endpoints)
    print("✅ Brute Force Protection enabled")


# Fonction helper pour les routes de login
def check_login_attempt(request: Request) -> None:
    """
    À appeler au début des routes de login
    Lève une HTTPException si l'IP est bloquée
    """
    ip = request.client.host if request.client else "unknown"
    
    if login_tracker.is_blocked(ip):
        remaining = login_tracker.get_block_time_remaining(ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many failed login attempts. Try again in {remaining} seconds."
        )

def record_login_failure(request: Request) -> None:
    """À appeler après un échec de login"""
    ip = request.client.host if request.client else "unknown"
    login_tracker.record_failed_attempt(ip)

def record_login_success(request: Request) -> None:
    """À appeler après un succès de login"""
    ip = request.client.host if request.client else "unknown"
    login_tracker.record_successful_attempt(ip)