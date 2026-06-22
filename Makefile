.PHONY: help install train run docker-up docker-down lint

help:
	@echo ""
	@echo "IMDB Movie Recommender:"
	@echo ""
	@echo "  make install - Instalacja zależności Python"
	@echo "  make train - Preprocessing danych + trening modelu"
	@echo "  make run - Uruchomienie API lokalnie (port 8008)"
	@echo "  make docker-up - Uruchomienie przez Docker Compose"
	@echo "  make docker-down - Zatrzymanie kontenerów"
	@echo "  make lint - Sprawdzenie jakości kodu (pylint)"
	@echo "  make streamlit - Uruchomienie interfejsu użytkownika (Streamlit)"
	@echo ""
	@echo "Wymaganie wstępne: umieść final_dataset.parquet w data/raw/"
	@echo ""

install:
	pip install -r requirements.txt

train:
	python model/train.py

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8008

docker-up:
	sudo docker-compose up --build

docker-down:
	sudo docker-compose down

lint:
	pylint app/ model/ data/preprocessing.py --fail-under=8

streamlit:
	streamlit run app/streamlit_app.py