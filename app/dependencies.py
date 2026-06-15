"""Fabryki zależności wstrzykiwane przez FastAPI (Depends)."""

from __future__ import annotations

from functools import lru_cache

from app.repository import RecommenderRepository
from app.service import RecommendationService


@lru_cache(maxsize=1)
def get_recommendation_service() -> RecommendationService:
    """Zwraca singleton serwisu rekomendacji."""
    return RecommendationService(RecommenderRepository())
