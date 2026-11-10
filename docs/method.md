# Method

## Problem

For each day *D*, using information available at midnight before *D*:

1. **Forecast** hourly demand (and, from v0.2, market prices) for the 24 hours of *D*.
2. **Decide** a battery schedule for *D*: charge and discharge in each hour, subject to the battery's energy capacity, power limit, round-trip efficiency and state-of-charge limits.
3. **Evaluate** the schedule against what actually happened, and against the schedule that perfect foresight would have chosen (*regret*).

## Data (v0.1)

- **Source:** U.S. EIA API v2, `electricity/rto/region-data`, type `D` (demand), hourly, by balancing authority. Values are MWh per hour.
- **Cleaning:** put the series on a complete hourly UTC grid; treat zero or negative values as missing; linearly interpolate gaps of up to 3 hours. Longer gaps stay missing, and interpolated hours are flagged and excluded from scoring.
- **Time:** stored in UTC; calendar features use local time (America/New_York) so hour-of-day and holidays line up with how people use electricity.

## Forecasting (v0.1)

Day-ahead baselines use only values at least 24 hours old:

| Baseline | Forecast for hour *t* |
|---|---|
| `naive_yesterday` | demand at *t* − 24 h |
| `seasonal_naive_week` | demand at *t* − 168 h (same hour, same weekday last week) |
| `same_hour_mean_7d` | mean of demand at *t* − 24 h, …, *t* − 168 h |

## Evaluation (v0.1)

Backtest over the most recent *N* days (default 90): MAE, RMSE and MAPE on non-imputed hours.

## Battery optimization (planned, v0.2)

Decision variables per hour *t*: charge *c_t* ≥ 0, discharge *d_t* ≥ 0, state of charge *s_t*.

- Energy balance: *s_t* = *s_{t-1}* + η_c *c_t* − *d_t* / η_d
- Limits: *c_t*, *d_t* ≤ *P*; *s_min* ≤ *s_t* ≤ *s_max*
- Objective (arbitrage): maximize Σ_t *p̂_t* (*d_t* − *c_t*) using forecast prices *p̂_t*, then score with actual prices.

Later versions add binary charge/discharge decisions (MILP), degradation cost, scenario-based stochastic optimization and a dynamic-programming policy.
