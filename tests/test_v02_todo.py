"""Tests to write for v0.2. Each is skipped until its module is built:
remove the skip mark, write the test, and make it pass."""
import pytest

todo = pytest.mark.skip(reason="v0.2: not built yet")


@todo
def test_weather_hourly_utc_no_duplicates():
    """fetch_weather returns one row per UTC hour."""


@todo
def test_degree_hours_nonnegative_and_exclusive():
    """cooling_dh and heating_dh are >= 0 and never both positive."""


@todo
def test_ml_features_have_no_lag_under_24h():
    """No feature used by the ML model looks less than 24 hours back."""


@todo
def test_ml_backtest_trains_only_on_past():
    """Every forecast day is predicted by a model trained on earlier data only."""


@todo
def test_lp_respects_power_and_soc_limits():
    """charge, discharge <= P; E_min <= soc <= E_max for every hour."""


@todo
def test_lp_energy_balance():
    """soc[t] - soc[t-1] == eta_c * c[t] - d[t] / eta_d, and the day ends at s_init."""


@todo
def test_peak_shaving_never_raises_peak():
    """The shaved peak is <= the original peak, with equality when the battery is empty."""


@todo
def test_arbitrage_flat_price_earns_nothing():
    """With a constant price and efficiency < 1, the best schedule is to do nothing."""


@todo
def test_regret_is_zero_for_perfect_forecast():
    """daily_regret with forecast == actual gives zero regret."""
