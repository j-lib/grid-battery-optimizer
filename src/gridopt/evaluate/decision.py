"""Decision metrics: how much forecast error costs (v0.2, issue: "Score decisions").

For each backtest day:
  1. Perfect foresight: optimize on the actual load (or price). Best possible.
  2. Forecast-driven: optimize on the forecast, then apply that schedule to actuals.
  3. Regret = perfect - forecast-driven, in MW of peak reduced (or dollars).

Compare regret for each forecast (baselines and ML). A forecast with lower MAPE
does not always have lower regret; that gap is the thesis question.
"""
from __future__ import annotations

import pandas as pd


def daily_regret(actual: pd.Series, forecast: pd.Series, battery, objective: str = "peak") -> pd.DataFrame:
    """Columns per day: perfect, achieved, regret."""
    raise NotImplementedError("v0.2: see GitHub issue 'Score decisions'")
