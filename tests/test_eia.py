import numpy as np
import pandas as pd
import pytest

from gridopt.data import eia


def _row(period, value):
    return {"period": period, "respondent": "DUK", "type": "D", "value": value, "value-units": "megawatthours"}


class FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


class FakeSession:
    """Serves a fixed list of rows in pages, like the EIA API."""

    def __init__(self, rows, page_size):
        self.rows, self.page_size, self.calls = rows, page_size, []

    def get(self, url, params, timeout):
        self.calls.append(params)
        start = params["offset"]
        page = self.rows[start:start + self.page_size]
        return FakeResponse({"response": {"total": str(len(self.rows)), "data": page}})


def test_parse_rows_handles_strings_and_duplicates():
    rows = [_row("2025-01-01T02", "11000"), _row("2025-01-01T00", 10000), _row("2025-01-01T02", "11500")]
    df = eia.parse_rows(rows)
    assert list(df.index.hour) == [0, 2]
    assert str(df.index.tz) == "UTC"
    assert df["demand_mwh"].tolist() == [10000.0, 11500.0]


def test_fetch_demand_pages_through_results(monkeypatch):
    monkeypatch.setattr(eia, "PAGE_SIZE", 2)
    rows = [_row(f"2025-01-01T{h:02d}", 10000 + h) for h in range(5)]
    session = FakeSession(rows, page_size=2)
    df = eia.fetch_demand("DUK", "2025-01-01", "2025-01-01T04", api_key="test", session=session)
    assert len(df) == 5
    assert [c["offset"] for c in session.calls] == [0, 2, 4]
    assert session.calls[0]["facets[respondent][]"] == "DUK"


def test_fetch_demand_requires_key(monkeypatch):
    monkeypatch.delenv("EIA_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="EIA_API_KEY"):
        eia.fetch_demand("DUK", "2025-01-01", "2025-01-02")


def test_clean_hourly_fills_short_gaps_only():
    idx = pd.date_range("2025-01-01", periods=12, freq="h", tz="UTC", name="timestamp")
    values = np.arange(100.0, 112.0)
    df = pd.DataFrame({"demand_mwh": values}, index=idx)
    # Two-hour gap (fillable), a zero reading, and a four-hour gap (left missing)
    df = df.drop(idx[[2, 3]])
    df.loc[idx[5], "demand_mwh"] = 0
    df = df.drop(idx[[7, 8, 9, 10]])

    out = eia.clean_hourly(df, max_gap_hours=3)
    assert len(out) == 12
    assert out.loc[idx[2], "demand_mwh"] == pytest.approx(102.0)
    assert out.loc[idx[5], "demand_mwh"] == pytest.approx(105.0)
    assert out.loc[idx[8], "demand_mwh"] != out.loc[idx[8], "demand_mwh"]  # NaN
    assert out["imputed"].sum() == 3


def test_save_and_load_round_trip(tmp_path, hourly_demand):
    path = eia.save(hourly_demand, tmp_path / "d.csv")
    back = eia.load(path)
    assert back.index.equals(hourly_demand.index)
    assert np.allclose(back["demand_mwh"], hourly_demand["demand_mwh"])
