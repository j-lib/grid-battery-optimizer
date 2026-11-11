"""Day-ahead battery schedule as a linear program (v0.2, issue: "Battery LP").

Decision variables for each hour t = 0..T-1:
    c[t] >= 0   charge power (MW)
    d[t] >= 0   discharge power (MW)
    s[t]        state of charge at end of hour t (MWh)

Constraints:
    c[t] <= P,  d[t] <= P
    s[t] = s[t-1] + eta_c * c[t] - d[t] / eta_d      (one-hour steps)
    E_min <= s[t] <= E_max
    s[T-1] = s_init                                    (end the day where it started)
with eta_c = eta_d = sqrt(round_trip_efficiency).

Objectives:
    peak shaving:  minimize  peak
                   subject to  load[t] + c[t] - d[t] <= peak   for all t
    arbitrage:     maximize  sum_t price[t] * (d[t] - c[t])

Solver: HiGHS through scipy.optimize.linprog (`pip install -e ".[opt]"`).
Note: c and d can both be positive in the same hour; with efficiency < 1 the
optimum avoids it, but add a test that checks it.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Battery:
    energy_mwh: float
    power_mw: float
    round_trip_efficiency: float = 0.90
    min_soc_fraction: float = 0.10
    max_soc_fraction: float = 0.95
    initial_soc_fraction: float = 0.50


@dataclass
class Schedule:
    charge_mw: np.ndarray
    discharge_mw: np.ndarray
    soc_mwh: np.ndarray
    objective: float


def peak_shaving(load_mw: np.ndarray, battery: Battery) -> Schedule:
    """Schedule that minimizes the highest net load of the day."""
    raise NotImplementedError("v0.2: see GitHub issue 'Battery LP'")


def arbitrage(price_usd_mwh: np.ndarray, battery: Battery) -> Schedule:
    """Schedule that maximizes revenue from buying low and selling high."""
    raise NotImplementedError("v0.2: see GitHub issue 'Battery LP'")


def apply_schedule(load_mw: np.ndarray, schedule: Schedule) -> np.ndarray:
    """Net load after the battery runs the schedule: load + charge - discharge."""
    return load_mw + schedule.charge_mw - schedule.discharge_mw
