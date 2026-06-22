"""Streamlit - interfejs użytkownika dla IMDB Movie Recommender.

Wywołuje istniejące API (FastAPI) przez HTTP, nie duplikuje logiki modelu.

Wymaga działającego API:
    make run            (lokalnie, port 8008)
    docker-compose up    (Docker, port 8000)

Uruchomienie:
    streamlit run app/streamlit_app.py
"""

from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8008")

st.set_page_config(page_title="IMDB Movie Recommender")

st.title("IMDB Movie Recommender")
st.caption("System rekomendacji filmów content-based")


def _api_available() -> bool:
    """Sprawdza, czy API odpowiada."""
    try:
        return requests.get(f"{API_URL}/health", timeout=2).status_code == 200
    except requests.exceptions.RequestException:
        return False


if not _api_available():
    st.error(
        f"API nie jest dostępne pod adresem {API_URL}. "
        "Uruchom najpierw: `make run` lub `docker-compose up`."
    )
    st.stop()

with st.form("recommend_form"):
    title = st.text_input("Tytuł filmu", placeholder="np. Inception")
    col1, col2 = st.columns(2)
    with col1:
        year = st.number_input(
            "Rok (opcjonalnie)",
            min_value=0, max_value=2030, value=0, step=1,
        )
    with col2:
        limit = st.slider("Liczba rekomendacji", min_value=1, max_value=20, value=5)
    submitted = st.form_submit_button("Szukaj rekomendacji")

if submitted:
    if not title.strip():
        st.warning("Podaj tytuł filmu.")
        st.stop()

    payload: dict = {"title": title.strip(), "limit": limit}
    if year > 0:
        payload["year"] = int(year)

    try:
        response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    except requests.exceptions.RequestException as exc:
        st.error(f"Błąd połączenia z API: {exc}")
        st.stop()

    if response.status_code == 404:
        st.warning(f"Nie znaleziono filmu „{title}” w bazie.")
    elif response.status_code == 503:
        st.error("Silnik rekomendacji jest niedostępny.")
    elif response.status_code != 200:
        st.error(f"Błąd API ({response.status_code}): {response.text}")
    else:
        results = response.json().get("results", [])
        if not results:
            st.info("Brak rekomendacji dla podanego filtru roku.")
        else:
            st.subheader(f"Top {len(results)} rekomendacji dla „{title}”")
            for movie in results:
                with st.container(border=True):
                    cols = st.columns([3, 1, 1])
                    cols[0].markdown(f"**{movie['title']}** ({movie['year']})")
                    cols[0].caption(movie["genres"])
                    cols[1].metric("Ocena IMDB", f"{movie['rating']:.1f}")
                    cols[2].metric("Podobieństwo", f"{movie['score']:.2f}")

st.divider()
with st.expander("Lista wszystkich filmów w bazie"):
    try:
        movies_response = requests.get(f"{API_URL}/movies", timeout=5)
        if movies_response.status_code == 200:
            st.dataframe(movies_response.json(), use_container_width=True)
    except requests.exceptions.RequestException:
        st.caption("Nie udało się wczytać listy filmów.")