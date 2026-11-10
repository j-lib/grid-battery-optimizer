"""Simple day-ahead baselines. Every later model must beat these to be worth using.

Each function takes an hourly demand series (UTC index) and returns a forecast series
on the same index, using only data at least 24 hours old.
"""
from __future__ import annotations

import pandas as pd


def _lagged(demand: pd.Series, hours: int) -> pd.Series:
    return demand.shift(freq=pd.Timedelta(hours=hours)).reindex(demand.index)


def naive_yesterday(demand: pd.Series) -> pd.Series:
    """Same hour yesterday."""
    return _lagged(demand, 24).rename("naive_yesterday")


def seasonal_naive_week(demand: pd.Series) -> pd.Series:
    """Same hour, same weekday last week (captures weekday/weekend differences)."""
    return _lagged(demand, 168).rename("seasonal_naive_week")


def same_hour_mean(demand: pd.Series, days: int = 7) -> pd.Series:
    """Average of the same hour over the previous `days` days."""
    lags = [_lagged(demand, 24 * d) for d in range(1, days + 1)]
    return pd.concat(lags, axis=1).mean(axis=1, skipna=True).rename(f"same_hour_mean_{days}d")


BASELINES = {
    "naive_yesterday": naive_yesterday,
    "seasonal_naive_week": seasonal_naive_week,
    "same_hour_mean_7d": same_hour_mean,
}
