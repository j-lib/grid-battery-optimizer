"""Wholesale electricity prices for the arbitrage version (v0.2, issue: "Add market prices").

Duke Energy Carolinas has no public hourly market price, so arbitrage uses a
market region. Plan: ERCOT day-ahead hub prices via the `gridstatus` library
(`pip install -e ".[prices]"`), with PJM as an alternative.
"""
from __future__ import annotations

import pandas as pd


def fetch_prices(market: str, location: str, start: str, end: str) -> pd.DataFrame:
    """Return hourly day-ahead prices indexed by UTC timestamp.

    Columns: price_usd_mwh. Negative prices are real and must be kept.
    """
    raise NotImplementedError("v0.2: see GitHub issue 'Add market prices'")
