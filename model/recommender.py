"""Content-based rekomendator filmowy (TF-IDF + cosine similarity)."""

from __future__ import annotations

import pathlib

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Domyślna ścieżka zapisu artefaktów modelu
ARTIFACTS_DIR = pathlib.Path(__file__).parent / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "recommender.pkl"

# Wagi nadawane poszczególnym polom w content stringu
# powtórzenie tekstu = wyższy IDF, co powoduje większą wagę)
_FIELD_REPEATS: dict[str, int] = {
    "genres": 4,
    "directors": 3,
    "stars": 2,
    "description": 1,
}


def _build_content_string(row: pd.Series) -> str:
    """Scala pola filmowe w jeden string z wagami przez powtórzenia."""
    parts: list[str] = []
    for field, repeats in _FIELD_REPEATS.items():
        value = row.get(field)
        if pd.isna(value) or str(value).strip() == "":
            continue
        # Normalizacja separatorów
        cleaned = (
            str(value)
            .replace(",", " ")
            .replace("|", " ")
            .strip()
        )
        parts.extend([cleaned] * repeats)
    return " ".join(parts)


class ContentRecommender:
    """Rekomendator filmów oparty na podobieństwie treści
    
    Atrybuty:
        _movies: DataFrame z kolumnami: title, year, genres, rating
                 oraz opcjonalnie directors, stars, description.
        _tfidf_matrix: Rzadka macierz TF-IDF (CSR), kształt (n_movies, n_features).
        _title_to_idx: Słownik {lowercase_title: row_index}.
    """

    def __init__(self) -> None:
        self._movies: pd.DataFrame | None = None
        self._tfidf_matrix = None
        self._title_to_idx: dict[str, int] = {}

    # Trening

    def fit(self, movies: pd.DataFrame) -> "ContentRecommender":
        """Wytrenuj rekomendator na DataFrame filmów.

        Args:
            movies: DataFrame z co najmniej kolumnami: title, year,
                    genres, rating. Opcjonalnie: directors, stars, description.
        Returns:
            self (umożliwia chain: recommender.fit(df).save())
        """
        self._movies = movies.reset_index(drop=True).copy()

        content_strings = self._movies.apply(_build_content_string, axis=1)

        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=25_000,
            sublinear_tf=True,
        )
        self._tfidf_matrix = vectorizer.fit_transform(content_strings)

        # Indeks tytułów (lowercase -> row index)
        self._title_to_idx = {
            title.strip().lower(): idx
            for idx, title in enumerate(self._movies["title"])
        }

        return self

    def recommend(
        self,
        title: str,
        top_k: int = 10,
        year: int | None = None,
    ) -> pd.DataFrame | None:
        """Zwróć top_k filmów podobnych do podanego tytułu.

        Args:
            title:  Tytuł filmu bazowego (case-insensitive).
            top_k:  Liczba rekomendacji do zwrócenia.
            year:   Jeśli podany filtruje wyniki do ±15 lat od roku
                    podanego (film bazowy zawsze wyłączony z wyników).

        Returns:
            DataFrame z kolumnami: title, year, genres, rating, score
            lub None jeśli tytułu nie ma w bazie.
        """
        if self._movies is None or self._tfidf_matrix is None:
            raise RuntimeError("Model nie został wytrenowany. Wywołaj fit() lub load().")

        key = title.strip().lower()
        if key not in self._title_to_idx:
            return None

        query_idx = self._title_to_idx[key]

        # Cosine similarity tylko dla wiersza zapytania
        scores: np.ndarray = linear_kernel(
            self._tfidf_matrix[query_idx], self._tfidf_matrix
        ).flatten()

        # Budowanie kandydatów (bez samego zapytania)
        candidate_mask = np.ones(len(self._movies), dtype=bool)
        candidate_mask[query_idx] = False

        if year is not None:
            year_diff = np.abs(self._movies["year"].to_numpy() - year)
            candidate_mask &= year_diff <= 15

        candidate_indices = np.where(candidate_mask)[0]
        candidate_scores = scores[candidate_indices]

        # Sortowanie malejące po score, bierzemy top_k
        sorted_order = np.argsort(candidate_scores)[::-1][:top_k]
        top_indices = candidate_indices[sorted_order]
        top_scores = candidate_scores[sorted_order]

        result = self._movies.iloc[top_indices][
            ["title", "year", "genres", "rating"]
        ].copy()
        result["score"] = np.round(top_scores, 4)
        result["genres"] = (
            result["genres"]
            .fillna("")
            .str.replace(r"\s*,\s*", ", ", regex=True)
        )

        return result.reset_index(drop=True)

    def list_movies(self) -> list[dict]:
        """Zwróć pełną listę filmów jako listę słowników {title, year}."""
        if self._movies is None:
            return []
        return self._movies[["title", "year"]].to_dict("records")

    # zapis modelu

    def save(self, path: pathlib.Path = MODEL_PATH) -> None:
        """Zapisz model na dysk (joblib).

        Args:
            path: Ścieżka docelowa. Katalog zostanie utworzony automatycznie.
        """
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "movies": self._movies,
            "tfidf_matrix": self._tfidf_matrix,
            "title_to_idx": self._title_to_idx,
        }
        joblib.dump(payload, path, compress=3)
        size_mb = path.stat().st_size / 1_048_576
        print(f"Model zapisany: {path}  ({size_mb:.1f} MB)")

    @classmethod
    def load(cls, path: pathlib.Path = MODEL_PATH) -> "ContentRecommender":
        """Wczytaj model z dysku.

        Args:
            path: Ścieżka do pliku .pkl.

        Raises:
            FileNotFoundError: Jeśli plik nie istnieje (model nie wytrenowany).
        """
        path = pathlib.Path(path)
        if not path.exists():
            raise FileNotFoundError(
                f"Artefakty modelu nie istnieją: {path}\n"
                "Uruchom najpierw: python model/train.py"
            )
        payload = joblib.load(path)
        instance = cls()
        instance._movies = payload["movies"]
        instance._tfidf_matrix = payload["tfidf_matrix"]
        instance._title_to_idx = payload["title_to_idx"]
        return instance
