"""Calendar and lag features for day-ahead demand forecasting.

All lag features are at least 24 hours old, so they are known when a day-ahead
forecast is issued at midnight (no look-ahead leakage).
"""
from __future__ import annotations

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar


def calendar_features(index: pd.DatetimeIndex, timezone: str = "America/New_York") -> pd.DataFrame:
    """Hour, weekday, month and holiday indicators in local time."""
    local = index.tz_convert(timezone)
    holidays = USFederalHolidayCalendar().holidays(start=local.min().date(), end=local.max().date())
    local_dates = local.normalize().tz_localize(None)
    return pd.DataFrame({
        "hour": local.hour,
        "dayofweek": local.day_of_week,
        "month": local.month,
        "is_weekend": (local.day_of_week >= 5).astype(int),
        "is_holiday": local_dates.isin(holidays).astype(int),
    }, index=index)


def lag_features(demand: pd.Series, lags_hours: tuple[int, ...] = (24, 48, 168)) -> pd.DataFrame:
    """Demand at fixed lags (in hours) and a 7-day rolling mean of the 24-hour lag."""
    out = {f"lag_{h}h": demand.shift(freq=pd.Timedelta(hours=h)).reindex(demand.index) for h in lags_hours}
    lag24 = demand.shift(freq=pd.Timedelta(hours=24)).reindex(demand.index)
    out["lag24_mean_7d"] = lag24.rolling("7D", min_periods=24).mean()
    return pd.DataFrame(out, index=demand.index)


def build_features(df: pd.DataFrame, timezone: str = "America/New_York") -> pd.DataFrame:
    """Target plus all features, aligned on the same hourly index."""
    feats = pd.concat([calendar_features(df.index, timezone), lag_features(df["demand_mwh"])], axis=1)
    return pd.concat([df[["demand_mwh"]], feats], axis=1)
