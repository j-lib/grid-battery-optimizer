"""Streamlit demo (v1): actual demand vs. baseline day-ahead forecasts.

Run locally:  pip install -e ".[app]"  then  streamlit run app/streamlit_app.py
Needs data from `gridopt fetch` first.
"""
from pathlib import Path

import pandas as pd
import streamlit as st

from gridopt import pipeline
from gridopt.config import load_config
from gridopt.data import eia

st.set_page_config(page_title="Grid Battery Optimizer", layout="wide")
st.title("Grid Battery Optimizer")
st.caption("v1: day-ahead electricity demand forecasting baselines. Battery optimization arrives in v2.")

cfg = load_config()
path = pipeline.raw_path(cfg)
if not Path(path).exists():
    st.warning(f"No data at {path}. Run `gridopt fetch` first (needs a free EIA_API_KEY).")
    st.stop()

df = eia.load(path)
days = st.slider("Backtest window (days)", 14, 365, cfg["forecast"]["backtest_days"])
table, frame = pipeline.backtest_baselines(df, days)

st.subheader(f"Forecast accuracy, last {days} days ({cfg['data']['region']})")
st.dataframe(table.round(2))

tz = cfg["data"]["timezone"]
end = frame.index.max()
start = st.date_input("Week starting", (end - pd.Timedelta(days=7)).tz_convert(tz).date())
week = frame.loc[pd.Timestamp(start, tz=tz):pd.Timestamp(start, tz=tz) + pd.Timedelta(days=7)]
week.index = week.index.tz_convert(tz).tz_localize(None)
st.subheader("Actual vs. forecasts (MWh)")
st.line_chart(week)
