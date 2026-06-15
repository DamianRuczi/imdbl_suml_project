"""Wyjątki domenowe warstwy aplikacji."""

from __future__ import annotations


class MovieNotFoundError(Exception):
    """Zgłaszany, gdy film bazowy nie istnieje w zbiorze."""


class RecommenderUnavailableError(Exception):
    """Zgłaszany, gdy źródło rekomendacji jest niedostępne."""
