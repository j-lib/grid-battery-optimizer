"""End-to-end steps: fetch data, then backtest forecasts over the most recent days."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from gridopt.data import eia
from gridopt.evaluate import metrics
from gridopt.forecast.baselines import BASELINES


def raw_path(cfg: dict) -> Path:
    d = cfg["data"]
    return Path(d["raw_dir"]) / f"demand_{d['region']}.csv"


def fetch(cfg: dict) -> Path:
    d = cfg["data"]
    df = eia.fetch_demand(d["region"], d["start"], d["end"])
    df = eia.clean_hourly(df, max_gap_hours=d.get("max_gap_hours", 3))
    return eia.save(df, raw_path(cfg))


def backtest_baselines(df: pd.DataFrame, backtest_days: int = 90) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Score each baseline over the last `backtest_days` days.

    Imputed hours are excluded from scoring. Returns (metrics table, forecasts frame).
    """
    demand = df["demand_mwh"]
    forecasts = {name: fn(demand) for name, fn in BASELINES.items()}

    cutoff = demand.index.max() - pd.Timedelta(days=backtest_days)
    window = demand.index > cutoff
    if "imputed" in df:
        window &= ~df["imputed"].astype(bool).to_numpy()

    actual = demand[window]
    scored = {k: v[window] for k, v in forecasts.items()}
    frame = pd.concat([demand.rename("actual"), *forecasts.values()], axis=1)
    return metrics.summary(actual, scored), frame
