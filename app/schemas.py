"""Modele danych Pydantic – kontrakty wejścia/wyjścia API."""

from __future__ import annotations

from pydantic import BaseModel, Field



class MovieItem(BaseModel):
    title: str
    year: int


class RecommendRequest(BaseModel):
    title: str
    year: int | None = Field(default=None, ge=1900, le=2030)
    limit: int = Field(default=10, ge=1, le=50)

class RecommendationMovieItem(MovieItem):
    genres: str
    rating: float
    score: float


class RecommendResponse(BaseModel):
    count: int
    results: list[RecommendationMovieItem]
