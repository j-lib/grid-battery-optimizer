"""Hourly electricity demand from the U.S. EIA (Form EIA-930) via the EIA API v2.

Get a free API key at https://www.eia.gov/opendata/register.php and set it as the
EIA_API_KEY environment variable (or put it in a local .env file, which git ignores).
"""
from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://api.eia.gov/v2/electricity/rto/region-data/data/"
PAGE_SIZE = 5000  # EIA API v2 maximum rows per request


def _api_key(api_key: str | None) -> str:
    key = api_key or os.environ.get("EIA_API_KEY")
    if not key:
        raise RuntimeError("Set the EIA_API_KEY environment variable (free key: https://www.eia.gov/opendata/)")
    return key


def fetch_demand(
    region: str,
    start: str,
    end: str,
    api_key: str | None = None,
    session: requests.Session | None = None,
) -> pd.DataFrame:
    """Download hourly demand (MWh) for one balancing authority.

    Returns a DataFrame with a UTC DatetimeIndex named 'timestamp' and a 'demand_mwh'
    column, sorted by time. Requests are paged because the API caps each response.
    """
    session = session or requests.Session()
    params = {
        "api_key": _api_key(api_key),
        "frequency": "hourly",
        "data[0]": "value",
        "facets[respondent][]": region,
        "facets[type][]": "D",  # D = demand
        "start": f"{pd.Timestamp(start):%Y-%m-%dT%H}",
        "end": f"{pd.Timestamp(end):%Y-%m-%dT%H}",
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
        "length": PAGE_SIZE,
    }

    rows: list[dict] = []
    offset = 0
    while True:
        resp = session.get(API_URL, params={**params, "offset": offset}, timeout=60)
        resp.raise_for_status()
        payload = resp.json()["response"]
        page = payload.get("data", [])
        rows.extend(page)
        total = int(payload.get("total", len(rows)))
        offset += len(page)
        if not page or offset >= total:
            break

    return parse_rows(rows)


def parse_rows(rows: list[dict]) -> pd.DataFrame:
    """Convert EIA API rows into a tidy hourly DataFrame."""
    if not rows:
        return pd.DataFrame({"demand_mwh": pd.Series(dtype=float)},
                            index=pd.DatetimeIndex([], tz="UTC", name="timestamp"))
    df = pd.DataFrame(rows)
    out = pd.DataFrame({
        "timestamp": pd.to_datetime(df["period"], format="%Y-%m-%dT%H", utc=True),
        "demand_mwh": pd.to_numeric(df["value"], errors="coerce"),
    })
    return (out.dropna(subset=["timestamp"])
               .drop_duplicates("timestamp", keep="last")
               .set_index("timestamp")
               .sort_index())


def clean_hourly(df: pd.DataFrame, max_gap_hours: int = 3) -> pd.DataFrame:
    """Put the series on a complete hourly grid and fill short gaps.

    - Adds missing hours as NaN.
    - Treats zero or negative demand as missing (reporting errors in EIA-930 data).
    - Linearly interpolates gaps of up to `max_gap_hours`; longer gaps stay NaN.
    - Adds an 'imputed' flag so filled values can be excluded from evaluation.
    """
    if df.empty:
        return df.assign(imputed=pd.Series(dtype=bool))
    full_index = pd.date_range(df.index.min(), df.index.max(), freq="h", tz="UTC", name="timestamp")
    s = df["demand_mwh"].reindex(full_index)
    s = s.where(s > 0)
    missing = s.isna()

    # Interpolate only runs of missing values no longer than max_gap_hours
    run_id = (missing != missing.shift()).cumsum()
    run_len = missing.groupby(run_id).transform("sum")
    fillable = missing & (run_len <= max_gap_hours)
    filled = s.interpolate(method="time", limit_area="inside")
    s = s.where(~fillable, filled)

    return pd.DataFrame({"demand_mwh": s, "imputed": fillable & s.notna()})


def save(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path)
    return path


def load(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path, index_col="timestamp", parse_dates=["timestamp"])
    df.index = pd.DatetimeIndex(df.index, tz="UTC") if df.index.tz is None else df.index.tz_convert("UTC")
    return df
