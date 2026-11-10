import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def hourly_demand():
    """Six weeks of synthetic hourly demand with daily and weekly cycles."""
    idx = pd.date_range("2025-03-01", periods=24 * 42, freq="h", tz="UTC", name="timestamp")
    hours = np.arange(len(idx))
    daily = 1500 * np.sin(2 * np.pi * (hours % 24) / 24)
    weekly = np.where(idx.day_of_week >= 5, -800, 0)
    rng = np.random.default_rng(0)
    demand = 12000 + daily + weekly + rng.normal(0, 100, len(idx))
    return pd.DataFrame({"demand_mwh": demand, "imputed": False}, index=idx)
