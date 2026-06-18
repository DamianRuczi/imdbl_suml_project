"""Warstwa repozytorium: źródło danych dla rekomendacji.

Przy starcie próbuje wczytać wytrenowany ContentRecommender
z model/artifacts/recommender.pkl.

Jeśli plik nie istnieje (model jeszcze nie wytrenowany), repozytorium
działa na danych atrapowych i loguje ostrzeżenie, gdy API odpowiada normalnie
z danymi mock zamiast crashować.
"""

from __future__ import annotations

import logging
import pathlib

from app.exceptions import RecommenderUnavailableError

logger = logging.getLogger(__name__)

_MODEL_PATH = (
    pathlib.Path(__file__).parent.parent / "model" / "artifacts" / "recommender.pkl"
)

# Dane mock (fallback gdy model nie jest wytrenowany)
_MOCK_CATALOG = [
    {"title": "Inception", "year": 2010},
    {"title": "The Matrix", "year": 1999},
    {"title": "Interstellar", "year": 2014},
    {"title": "The Dark Knight", "year": 2008},
    {"title": "Pulp Fiction", "year": 1994},
]

_MOCK_RECOMMENDATIONS = [
    {"title": "Interstellar", "year": 2014, "genres": "Sci-Fi, Drama",
     "rating": 8.6, "score": 0.91},
    {"title": "The Matrix", "year": 1999, "genres": "Sci-Fi, Action",
     "rating": 8.7, "score": 0.88},
    {"title": "Memento", "year": 2000, "genres": "Mystery, Thriller",
     "rating": 8.4, "score": 0.85},
    {"title": "The Prestige", "year": 2006, "genres": "Drama, Mystery",
     "rating": 8.5, "score": 0.83},
    {"title": "Shutter Island", "year": 2010, "genres": "Mystery, Thriller",
     "rating": 8.2, "score": 0.80},
    {"title": "Blade Runner 2049", "year": 2017, "genres": "Sci-Fi, Drama",
     "rating": 8.0, "score": 0.78},
    {"title": "Arrival", "year": 2016, "genres": "Sci-Fi, Drama",
     "rating": 7.9, "score": 0.76},
    {"title": "Tenet", "year": 2020, "genres": "Sci-Fi, Action",
     "rating": 7.3, "score": 0.74},
]


def _try_load_recommender():
    """Próbuje wczytać model; zwraca instancję lub None."""
    try:
        from model.recommender import ContentRecommender
        recommender = ContentRecommender.load(_MODEL_PATH)
        logger.info("ContentRecommender wczytany z %s", _MODEL_PATH)
        return recommender
    except FileNotFoundError:
        logger.warning(
            "Artefakty modelu nie istnieją (%s). "
            "Używam danych mock. Uruchom `python model/train.py` aby wytrenować model.",
            _MODEL_PATH,
        )
        return None
    except Exception as exc:
        logger.error("Błąd wczytywania modelu: %s. Używam danych mock.", exc)
        return None


class RecommenderRepository:
    """Repozytorium danych dla serwisu rekomendacji.

    Przy inicjalizacji próbuje załadować wytrenowany model.
    Jeśli model niedostępny, transparentnie przełącza się na dane mock.
    """

    def __init__(self) -> None:
        self._recommender = _try_load_recommender()
        self._using_mock: bool = self._recommender is None

    @property
    def using_mock(self) -> bool:
        """True jeśli model nie jest dostępny i aplikacja używa danych mock."""
        return self._using_mock

    def list_movies(self) -> list[dict]:
        """Zwróć listę wszystkich filmów."""
        if self._using_mock:
            return list(_MOCK_CATALOG)
        return self._recommender.list_movies()

    def recommend(
        self,
        title: str,
        top_k: int,
        year: int | None = None,
    ) -> list[dict] | None:
        """Zwróć rekomendacje dla podanego tytułu.

        Returns:
            Lista słowników z polami: title, year, genres, rating, score.
            None jeśli tytułu nie ma w bazie.

        Raises:
            RecommenderUnavailableError: Jeśli model jest niedostępny
                                         i żądanie nie może być obsłużone przez mock.
        """
        if self._using_mock:
            # Mock zawsze zwraca wyniki (ignoruje title)
            return list(_MOCK_RECOMMENDATIONS[:top_k])

        result_df = self._recommender.recommend(
            title=title,
            top_k=top_k,
            year=year,
        )
        if result_df is None:
            return None

        return result_df.to_dict("records")