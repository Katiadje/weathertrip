from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

def add_security_headers(app: FastAPI):
    """Ajoute les headers de sécurité"""
    
    @app.middleware("http")
    async def security_headers_middleware(request, call_next):
        response = await call_next(request)
        
        # Protection XSS
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        # HTTPS strict
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

def setup_cors(app: FastAPI):
    """Configure CORS de manière sécurisée"""
    
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # Jamais "*" en prod !
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
        max_age=600,  # Cache preflight 10 min
    )

def setup_security_middleware(app: FastAPI):
    """Configure tous les middlewares de sécurité"""
    
    # CORS
    setup_cors(app)
    
    # Headers de sécurité
    add_security_headers(app)
    
    # Protection contre les host headers malveillants
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    )