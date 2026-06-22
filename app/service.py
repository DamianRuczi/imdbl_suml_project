"""Warstwa serwisu – logika biznesowa rekomendacji filmów."""

from __future__ import annotations

from app.exceptions import MovieNotFoundError
from app.repository import RecommenderRepository
from app.schemas import MovieItem, RecommendationMovieItem, RecommendRequest, RecommendResponse


class RecommendationService:
    """Łączy warstwę repozytorium z kontraktami API (DTO)."""

    def __init__(self, repository: RecommenderRepository) -> None:
        self._repository = repository

    def list_movies(self) -> list[MovieItem]:
        """Zwraca listę wszystkich filmów jako modele Pydantic."""
        rows = self._repository.list_movies()
        return [MovieItem(**row) for row in rows]

    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """Zwraca rekomendacje dla tytułu podanego w żądaniu.

        Raises:
            MovieNotFoundError: Jeśli tytuł nie istnieje w bazie.
        """
        rows = self._repository.recommend(
            title=request.title,
            top_k=request.limit,
            year=request.year,
        )
        if rows is None:
            raise MovieNotFoundError(request.title)

        results = [RecommendationMovieItem(**row) for row in rows]
        return RecommendResponse(
            count=len(results),
            results=results,
        )
