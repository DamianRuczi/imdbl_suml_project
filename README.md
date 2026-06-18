# IMDB Movie Recommender

System rekomendacji filmów oparty na podejściu content-based filtering.
Dla podanego tytułu zwraca listę podobnych filmów na podstawie gatunków,
reżysera, obsady i opisu — bez potrzeby historii użytkownika.

## Technologie

- **FastAPI** – serwowanie API REST
- **scikit-learn** – TF-IDF + cosine similarity
- **pandas** – przetwarzanie danych
- **Docker** – konteneryzacja

## Struktura projektu

```
.
├── app/          # Warstwa API (FastAPI)
├── data/         # Preprocessing i EDA
│   └── raw/      # Surowy dataset (nie w repo – patrz niżej)
├── model/        # Model rekomendacji
│   ├── recommender.py  # Klasa ContentRecommender
│   └── train.py        # Skrypt trenowania
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Uruchomienie

### Wymaganie wstępne – dataset

Dataset pochodzi z Kaggle i ze względu na licencję nie jest dołączony do repozytorium.

1. Pobierz plik `final_dataset.parquet` z:  
   https://www.kaggle.com/datasets/raedaddala/imdb-movies-from-1960-to-2023

2. Umieść go w katalogu:
   ```
   data/raw/final_dataset.parquet
   ```

### Opcja A – Docker (zalecana)

```bash
# 1. Wytrenuj model (jednorazowo, przed pierwszym uruchomieniem)
docker-compose run --rm api python model/train.py

# 2. Uruchom API
docker-compose up
```

API dostępne pod: http://localhost:8000

### Opcja B – lokalnie

```bash
# 1. Utwórz środowisko wirtualne i zainstaluj zależności
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# .venv\Scripts\activate       # Windows

pip install -r requirements.txt

# 2. Wytrenuj model
make train
# lub: python model/train.py

# 3. Uruchom API
make run
# lub: uvicorn app.main:app --reload --port 8000
```

## Endpointy API

| Metoda | Endpoint     | Opis                              |
|--------|--------------|-----------------------------------|
| GET    | `/health`    | Status aplikacji                  |
| GET    | `/movies`    | Lista wszystkich filmów w bazie   |
| POST   | `/recommend` | Rekomendacje dla podanego tytułu  |
| GET    | `/docs`      | Interaktywna dokumentacja Swagger |

### Przykład zapytania

```bash
curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d '{"title": "Inception", "limit": 5}'
```

### Przykład odpowiedzi

```json
{
  "count": 5,
  "results": [
    {
      "title": "Interstellar",
      "year": 2014,
      "genres": "Sci-Fi, Drama",
      "rating": 8.6,
      "score": 0.91
    }
  ]
}
```

Parametr `year` jest opcjonalny — jeśli podany, filtruje wyniki do ±15 lat.

## Model ML

`ContentRecommender` łączy pola tekstowe każdego filmu w jeden ciąg z wagami:

| Pole        | Waga |
|-------------|------|
| genres      | ×4   |
| directors   | ×3   |
| stars       | ×2   |
| description | ×1   |

Następnie wektoryzuje je TF-IDF (bigramy, max 25 000 cech) i oblicza cosine similarity.
Wytrenowany model zapisywany jest do `model/artifacts/recommender.pkl`.