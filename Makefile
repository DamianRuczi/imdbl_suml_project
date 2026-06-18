.PHONY: help install train run docker-up docker-down lint

help:
	@echo ""
	@echo "IMDB Movie Recommender – dostępne komendy:"
	@echo ""
	@echo "  make install     Instalacja zależności Python"
	@echo "  make train       Preprocessing danych + trening modelu"
	@echo "  make run         Uruchomienie API lokalnie (port 8000)"
	@echo "  make docker-up   Uruchomienie przez Docker Compose"
	@echo "  make docker-down Zatrzymanie kontenerów"
	@echo "  make lint        Sprawdzenie jakości kodu (pylint)"
	@echo ""

install:
	pip install -r requirements.txt

train:
	python model/train.py

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8008

docker-up:
	docker-compose up --build

docker-down:
	docker-compose down

lint:
	pylint app/ model/ data/preprocessing.py --fail-under=8