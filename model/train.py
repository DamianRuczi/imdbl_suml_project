from __future__ import annotations

import sys
import pathlib
import time

# Umożliwia importy z katalogu głównego projektu
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from data.preprocessing import (
    PROCESSED_DIR,
    load_raw,
    load_processed,
    preprocess,
    save_processed,
)
from model.recommender import ContentRecommender


def _ensure_processed_data() -> None:
    """Sprawdź czy przetworzone dane istnieją; jeśli nie - uruchom preprocessing."""
    processed_path = PROCESSED_DIR / "movies_clean.parquet"
    if not processed_path.exists():
        print("Przetworzone dane nie istnieją - uruchamiam preprocessing...")
        raw_df = load_raw()
        clean_df = preprocess(raw_df)
        save_processed(clean_df)
    else:
        print(f"Przetworzone dane znalezione: {processed_path}")


def main() -> None:
    """Główna funkcja trenująca i zapisująca model."""
    print("IMDB Movie Recommender - training model")

    # Dane
    _ensure_processed_data()
    movies = load_processed()

    # Trening
    print("\nTrenuję ContentRecommender...")
    start = time.perf_counter()
    recommender = ContentRecommender()
    recommender.fit(movies)
    elapsed = time.perf_counter() - start
    print(f"Trening zakończony w {elapsed:.1f} s")

    # Szybki test
    print("\nTest rekomendacji dla 'Inception':")
    result = recommender.recommend("Inception", top_k=5)
    if result is not None:
        print(result.to_string(index=False))
    else:
        print("Film 'Inception' nie znaleziony w bazie")

    # Zapis
    print()
    recommender.save()
    print("\nModel zapisany")


if __name__ == "__main__":
    main()