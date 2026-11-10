"""Forecast error metrics. Rows where either value is missing are ignored."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _align(actual: pd.Series, forecast: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    both = pd.concat([actual, forecast], axis=1).dropna()
    return both.iloc[:, 0].to_numpy(float), both.iloc[:, 1].to_numpy(float)


def mae(actual: pd.Series, forecast: pd.Series) -> float:
    a, f = _align(actual, forecast)
    return float(np.mean(np.abs(a - f))) if a.size else float("nan")


def rmse(actual: pd.Series, forecast: pd.Series) -> float:
    a, f = _align(actual, forecast)
    return float(np.sqrt(np.mean((a - f) ** 2))) if a.size else float("nan")


def mape(actual: pd.Series, forecast: pd.Series) -> float:
    """Mean absolute percentage error, in percent. Demand is always positive here."""
    a, f = _align(actual, forecast)
    return float(100 * np.mean(np.abs((a - f) / a))) if a.size else float("nan")


def summary(actual: pd.Series, forecasts: dict[str, pd.Series]) -> pd.DataFrame:
    """One row per forecast: MAE, RMSE, MAPE and the number of hours scored."""
    rows = []
    for name, fc in forecasts.items():
        a, _ = _align(actual, fc)
        rows.append({"model": name, "mae_mwh": mae(actual, fc), "rmse_mwh": rmse(actual, fc),
                     "mape_pct": mape(actual, fc), "hours": int(a.size)})
    return pd.DataFrame(rows).set_index("model").sort_values("mae_mwh")
