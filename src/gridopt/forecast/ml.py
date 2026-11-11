"""Gradient-boosting day-ahead forecast (v0.2, issue: "Gradient-boosting forecast").

Uses LightGBM (`pip install -e ".[ml]"`). Imported lazily so the base package
and CI do not need it.

Rules:
- Lags must be >= 24 hours (day-ahead, no look-ahead). Reuse features/build.py.
- Train only on data before each forecast day (rolling or expanding window).
- Report on the same 90-day window as the baselines. Target to beat:
  naive_yesterday, MAPE 6.32%, MAE 841 MWh (README, Nov 11 2026 run).
"""
from __future__ import annotations

import pandas as pd


def train(features: pd.DataFrame, target: pd.Series, params: dict | None = None):
    """Fit and return a LightGBM regressor."""
    raise NotImplementedError("v0.2: see GitHub issue 'Gradient-boosting forecast'")


def backtest(df: pd.DataFrame, backtest_days: int, retrain_every_days: int = 7) -> pd.DataFrame:
    """Day-by-day backtest. Returns columns: actual, forecast (hourly, UTC index)."""
    raise NotImplementedError("v0.2: see GitHub issue 'Gradient-boosting forecast'")
