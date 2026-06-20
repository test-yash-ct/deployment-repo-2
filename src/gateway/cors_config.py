from __future__ import annotations
import os

CORS_BASE_CONFIG = {
    "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    "allow_headers": ["*"],
    "expose_headers": ["*"],
    "max_age": 600,
}


def get_cors_origins(environment: str) -> list[str] | str:
    """Get CORS allowed origins based on environment.
    
    For production, returns explicit allowlist from CORS_ALLOWED_ORIGINS env var.
    For non-production, returns localhost development origins.
    """
    if environment in ("dev", "staging", "local", "test"):
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
        ]
