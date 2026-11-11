# Grid Battery Optimizer

![tests](https://github.com/j-lib/grid-battery-optimizer/actions/workflows/ci.yml/badge.svg)
![python](https://img.shields.io/badge/python-3.10%2B-blue)

Forecast electricity demand and prices, then decide when a grid battery should charge and discharge, while accounting for forecast uncertainty.

> **Status: v0.1, forecasting baselines.** Battery optimization arrives in v0.2. See the [roadmap](#roadmap).

## Why

Grid batteries earn their value by charging when power is cheap or plentiful and discharging when it is expensive or scarce. Doing that well takes two things: a good forecast of the next day, and a good decision under the forecast's uncertainty. U.S. battery storage is being built at record pace, and Duke Energy's 2026 Carolinas Resource Plan calls for about 13 GW of new storage over 15 years, so this "predict, then optimize" problem is growing quickly.

## How it works

```
EIA hourly demand ─▶ clean ─▶ features ─▶ forecast ─▶ optimize battery ─▶ backtest & evaluate
   (data/)                  (features/)  (forecast/)    (optimize/, v0.2)    (simulate/, evaluate/)
```

- **Data:** hourly demand by balancing authority from the U.S. EIA (Form EIA-930), default region Duke Energy Carolinas (`DUK`).
- **Forecasts:** day-ahead (issued with data through the previous day). Every model is compared against simple baselines, and later models must beat them.
- **Evaluation:** forecast error now; battery savings and regret against a perfect-foresight schedule from v0.2.

## Quick start

```bash
git clone https://github.com/j-lib/grid-battery-optimizer.git
cd grid-battery-optimizer
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev,app]"

cp .env.example .env              # then add your free EIA key: https://www.eia.gov/opendata/register.php
gridopt fetch                      # download and clean demand for the configured region
gridopt baseline                   # backtest the baseline forecasts
streamlit run app/streamlit_app.py # interactive view
pytest                             # run the tests
```

Settings (region, dates, backtest length, battery specs) live in [`config/default.yaml`](config/default.yaml).

## Results

First real-data run (Nov 11, 2026): hourly demand for Duke Energy Carolinas (EIA region `DUK`), Jan 2024 – Oct 2026, scored on the last 90 days (2,160 hours, Aug–Oct 2026).

| Baseline | MAE (MWh) | RMSE (MWh) | MAPE |
|---|---:|---:|---:|
| **Naive yesterday** (same hour, previous day) | **841** | **1,193** | **6.3%** |
| Same-hour mean, last 7 days | 1,146 | 1,550 | 8.8% |
| Seasonal naive (same hour, last week) | 1,491 | 2,049 | 11.4% |

**Takeaways**
- Yesterday's load is the best simple predictor: demand follows the weather, and weather changes more over a week than over a day.
- The weekly pattern matters less here than recent conditions, so averaging or lagging by a full week loses accuracy during the late-summer-to-fall transition.
- **The bar for v0.2:** a forecast has to beat 6.3% MAPE and 841 MWh MAE on the same 90 days to be worth adding.

Reproduce with `gridopt fetch` then `gridopt baseline --out results/baselines.csv`.

## Project structure

```
config/            Settings (no hard-coded numbers in code)
src/gridopt/
  data/            EIA download, cleaning, gap handling
  features/        Calendar and lag features (no look-ahead)
  forecast/        Baselines now; ML, statistical and probabilistic models later
  evaluate/        Error metrics; decision metrics later
  pipeline.py      End-to-end steps
  cli.py           `gridopt` command
app/               Streamlit demo
tests/             Unit tests (run in CI on every push)
docs/              Method and design decisions
notebooks/         Exploration only; finished code moves into src/
```

## Roadmap

| Version | Adds | Status |
|---|---|---|
| **v0.1** | EIA data pipeline, calendar and lag features, baseline forecasts, metrics, tests, CI, Streamlit view; first real-data results | ✅ |
| **v0.2** | Gradient-boosting forecasts; battery model; day-ahead LP schedule; market prices (PJM or ERCOT); backtested savings; Monte Carlo testing | ⏳ |
| **v0.3** | Mixed-integer scheduling, scenario-based stochastic optimization, dynamic-programming policy, probabilistic forecasts | |
| **v0.4** | Statistical time-series benchmarks, database backend, decision-focused learning experiments | |

## Docs

- [Method](docs/method.md): problem setup, forecasting approach, evaluation
- [Design decisions](docs/decisions.md): why each choice was made

## License

MIT. See [LICENSE](LICENSE).
