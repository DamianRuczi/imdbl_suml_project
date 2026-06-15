"""Warstwa repozytorium: źródło danych dla rekomendacji.

OBECNIE zwraca dane atrapowe (mocki), aby branch API ruszył zanim powstanie
wytrenowany model. Docelowo każda metoda załaduje i odpyta realny
`model.recommender.ContentRecommender` – miejsca podmiany oznaczone `# TODO`.

Repozytorium operuje na prostych słownikach; mapowanie na DTO należy do
warstwy serwisu.
"""

from __future__ import annotations

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


class RecommenderRepository:
    def list_movies(self) -> list[dict]:
        # TODO: zwrócić recommender.list_movies() po podpięciu modelu.

        return list(_MOCK_CATALOG)

    def recommend(
        self,
        title: str,
        top_k: int,
        year: int | None = None,
    ) -> list[dict] | None:
        # TODO: załadować model (recommender.load) i zwrócić recommender.recommend(title, top_k, year).to_dict("records").
        return list(_MOCK_RECOMMENDATIONS[:top_k])

