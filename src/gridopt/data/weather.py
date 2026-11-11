"""Hourly weather for the forecast (v0.2, issue: "Add weather data").

Source: Open-Meteo (https://open-meteo.com), free and keyless.
- Historical actuals:   https://archive-api.open-meteo.com/v1/archive
- Historical forecasts: https://historical-forecast-api.open-meteo.com/v1/forecast
  (what a forecaster would actually have known the day before; use these for
  an honest day-ahead backtest, see docs/decisions.md)

Locations come from config `weather.locations`. Store in UTC like the demand data.
"""
from __future__ import annotations

import pandas as pd

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
VARIABLES = ["temperature_2m", "relative_humidity_2m"]


def fetch_weather(lat: float, lon: float, start: str, end: str, session=None) -> pd.DataFrame:
    """Return hourly weather indexed by UTC timestamp.

    Columns: temperature_c, humidity_pct. One row per hour, no duplicates.
    """
    raise NotImplementedError("v0.2: see GitHub issue 'Add weather data'")


def combine_locations(frames: dict[str, pd.DataFrame], weights: dict[str, float]) -> pd.DataFrame:
    """Weighted average of several cities into one service-area series."""
    raise NotImplementedError("v0.2: see GitHub issue 'Add weather data'")


def weather_features(weather: pd.DataFrame, base_temp_c: float = 18.3) -> pd.DataFrame:
    """Heating and cooling degree-hours and related features.

    cooling_dh = max(T - base, 0); heating_dh = max(base - T, 0).
    18.3 C = 65 F, the usual US degree-day base.
    """
    raise NotImplementedError("v0.2: see GitHub issue 'Add weather data'")
