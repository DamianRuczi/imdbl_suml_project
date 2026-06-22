"""Modele danych Pydantic – kontrakty wejścia/wyjścia API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MovieItem(BaseModel):
    """Podstawowe dane filmu zwracane przez /movies."""
    title: str
    year: int


class RecommendRequest(BaseModel):
    """Żądanie rekomendacji – tytuł bazowy oraz opcjonalne filtry."""
    title: str
    year: int | None = Field(default=None, ge=1900, le=2030)
    limit: int = Field(default=10, ge=1, le=50)


class RecommendationMovieItem(MovieItem):
    """Film rekomendowany wraz z metadanymi i wynikiem podobieństwa."""
    genres: str
    rating: float
    score: float


class RecommendResponse(BaseModel):
    """Odpowiedź endpointu /recommend."""
    count: int
    results: list[RecommendationMovieItem]
