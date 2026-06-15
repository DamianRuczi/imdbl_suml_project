from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status

from app.dependencies import get_recommendation_service
from app.exceptions import MovieNotFoundError, RecommenderUnavailableError
from app.schemas import MovieItem, RecommendRequest, RecommendResponse
from app.service import RecommendationService

app = FastAPI(
    title="IMDB Movie Recommender",
    description="System rekomendacji filmów content-based oparty na danych IMDB.",
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/movies", response_model=list[MovieItem])
def list_movies(
    service: RecommendationService = Depends(get_recommendation_service),
) -> list[MovieItem]:
    return service.list_movies()


@app.post("/recommend", response_model=RecommendResponse)
def recommend(
    request: RecommendRequest,
    service: RecommendationService = Depends(get_recommendation_service),
) -> RecommendResponse:
    try:
        return service.recommend(request)
    except MovieNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Nie znaleziono filmu: {error}",
        ) from error
    except RecommenderUnavailableError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Silnik rekomendacji jest niedostępny.",
        ) from error
