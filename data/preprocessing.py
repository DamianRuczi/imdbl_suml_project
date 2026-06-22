from __future__ import annotations

import pathlib
import ast

import pandas as pd

_DATA_DIR = pathlib.Path(__file__).parent
RAW_DIR = _DATA_DIR / "raw"
PROCESSED_DIR = _DATA_DIR / "processed"

_REQUIRED: list[str] = ["title", "year", "rating", "genres"]
_YEAR_MIN = 1960
_YEAR_MAX = 2025
_RATING_MIN = 1.0
_RATING_MAX = 10.0


def _parse_list_string(value) -> str:
    """Konwertuje string z listą Pythona na czysty tekst.

    Używa ast.literal_eval (nie regex!) ponieważ nazwiska z apostrofem
    (np. "O'Brien") powodują, że Python zapisuje je w podwójnych cudzysłowach.

    Przykład: "['Drama', \"O'Brien\"]" -> "Drama, O'Brien"
    """
    if pd.isna(value):
        return ""
    try:
        tokens = ast.literal_eval(str(value))
    except (ValueError, SyntaxError):
        return str(value).strip()
    if not isinstance(tokens, list):
        return str(value).strip()
    return ", ".join(str(t).strip() for t in tokens if str(t).strip())


def load_raw(filename: str = "final_dataset.parquet") -> pd.DataFrame:
    """Wczytaj surowy plik z katalogu data/raw/.

    Args:
        filename: Domyślnie final_dataset.parquet

    Raises:
        FileNotFoundError: Jeśli plik nie istnieje.
    """
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {path}")

    if path.suffix == ".parquet":
        df = pd.read_parquet(path)
    else:
        df = pd.read_csv(path, low_memory=False)

    print(f"Wczytano {len(df):,} wierszy, {len(df.columns)} kolumn z {path.name}")
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    """Oczyść i znormalizuj DataFrame.

    Args:
        df: Surowy DataFrame

    Returns:
        Oczyszczony DataFrame z kolumnami:
        title, year, rating, genres, directors, stars, description
    """
    # Wyciągnij rok z release_date
    df["year"] = pd.to_datetime(df["release_date"], errors="coerce").dt.year

    # Zachowaj tylko kolumny potrzebne modelowi
    keep = ["title", "year", "rating", "genres", "directors", "stars", "description"]
    df = df[[c for c in keep if c in df.columns]].copy()

    # Odrzuć wiersze z brakami w kolumnach wymaganych
    initial_count = len(df)
    df = df.dropna(subset=[c for c in _REQUIRED if c in df.columns])
    print(f"Usunięto {initial_count - len(df):,} wierszy z brakami w wymaganych kolumnach")

    # Filtrowanie zakresów
    df["year"] = df["year"].astype(int)
    df = df[df["year"].between(_YEAR_MIN, _YEAR_MAX)]
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")
    df = df[df["rating"].between(_RATING_MIN, _RATING_MAX)]

    # Parsowanie list-stringów: ['Drama', 'Musical'] -> Drama, Musical
    for col in ["genres", "directors", "stars"]:
        if col in df.columns:
            df[col] = df[col].apply(_parse_list_string)

    # Usunięcie duplikatów
    before_dedup = len(df)
    df = df.drop_duplicates(subset=["title", "year"], keep="first")
    print(f"Usunięto {before_dedup - len(df):,} duplikatów (title + year)")

    df = df.reset_index(drop=True)
    print(f"{len(df):,} filmów gotowych do treningu")
    return df


def load_processed(filename: str = "movies_clean.parquet") -> pd.DataFrame:
    """Wczytaj przetworzone dane z data/processed/.

    Raises:
        FileNotFoundError: Jeśli przetworzone dane nie istnieją.
    """
    path = PROCESSED_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Przetworzone dane nie istnieją: {path}")
    df = pd.read_parquet(path)
    print(f"{len(df):,} filmów z {path}")
    return df


def save_processed(
    df: pd.DataFrame, filename: str = "movies_clean.parquet"
) -> None:
    """Zapisz DataFrame do data/processed/ jako Parquet."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    path = PROCESSED_DIR / filename
    df.to_parquet(path, index=False)
    size_kb = path.stat().st_size / 1024
    print(f"{len(df):,} filmów zapisano -> {path}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    raw_df = load_raw()
    clean_df = preprocess(raw_df)
    save_processed(clean_df)
