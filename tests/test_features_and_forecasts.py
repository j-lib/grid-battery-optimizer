import numpy as np
import pandas as pd
import pytest

from gridopt.evaluate import metrics
from gridopt.features.build import build_features, calendar_features
from gridopt.forecast import baselines
from gridopt.pipeline import backtest_baselines


def test_calendar_features_use_local_time():
    idx = pd.DatetimeIndex(["2025-07-04 16:00", "2025-07-05 04:00"], tz="UTC")
    feats = calendar_features(idx, "America/New_York")
    assert feats["hour"].tolist() == [12, 0]          # UTC-4 in summer
    assert feats["is_holiday"].tolist() == [1, 0]      # July 4 local
    assert feats["is_weekend"].tolist() == [0, 1]      # Fri, Sat


def test_lag_features_have_no_lookahead(hourly_demand):
    feats = build_features(hourly_demand)
    t = hourly_demand.index[200]
    assert feats.loc[t, "lag_24h"] == hourly_demand["demand_mwh"].loc[t - pd.Timedelta(hours=24)]
    assert np.isnan(feats["lag_168h"].iloc[0])


def test_baselines_are_shifted_copies(hourly_demand):
    d = hourly_demand["demand_mwh"]
    t = d.index[500]
    assert baselines.naive_yesterday(d).loc[t] == d.loc[t - pd.Timedelta(hours=24)]
    assert baselines.seasonal_naive_week(d).loc[t] == d.loc[t - pd.Timedelta(hours=168)]
    expected = np.mean([d.loc[t - pd.Timedelta(days=k)] for k in range(1, 8)])
    assert baselines.same_hour_mean(d).loc[t] == pytest.approx(expected)


def test_metrics_known_values():
    a = pd.Series([100.0, 200.0, 300.0])
    f = pd.Series([110.0, 190.0, np.nan])
    assert metrics.mae(a, f) == pytest.approx(10.0)
    assert metrics.rmse(a, f) == pytest.approx(10.0)
    assert metrics.mape(a, f) == pytest.approx(7.5)


def test_weekly_baseline_beats_yesterday_on_weekly_pattern(hourly_demand):
    table, frame = backtest_baselines(hourly_demand, backtest_days=21)
    assert set(table.index) == set(baselines.BASELINES)
    assert table.loc["seasonal_naive_week", "mae_mwh"] < table.loc["naive_yesterday", "mae_mwh"]
    assert (table["hours"] == 21 * 24).all()
    assert "actual" in frame
