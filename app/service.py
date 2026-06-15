from __future__ import annotations

from app.exceptions import MovieNotFoundError
from app.repository import RecommenderRepository
from app.schemas import MovieItem, RecommendationMovieItem, RecommendRequest, RecommendResponse


class RecommendationService:

    def __init__(self, repository: RecommenderRepository) -> None:
        self._repository = repository

    def list_movies(self) -> list[MovieItem]:
        rows = self._repository.list_movies()
        return [MovieItem(**row) for row in rows]

    def recommend(self, request: RecommendRequest) -> RecommendResponse:
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
