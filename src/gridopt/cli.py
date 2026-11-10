"""Command-line interface.

    gridopt fetch      # download and clean EIA demand for the configured region
    gridopt baseline   # backtest the baseline forecasts and save the metrics
"""
from __future__ import annotations

import argparse
from pathlib import Path

from gridopt import pipeline
from gridopt.config import load_config
from gridopt.data import eia


def _load_dotenv(path: str = ".env") -> None:
    """Read KEY=VALUE lines from a local .env file into the environment (if not already set)."""
    import os
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gridopt")
    parser.add_argument("--config", help="path to a YAML config (default: config/default.yaml)")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fetch", help="download and clean hourly demand from EIA")
    bl = sub.add_parser("baseline", help="backtest baseline day-ahead forecasts")
    bl.add_argument("--out", default="results/baseline_metrics.csv")
    args = parser.parse_args(argv)

    _load_dotenv()
    cfg = load_config(args.config)

    if args.command == "fetch":
        path = pipeline.fetch(cfg)
        print(f"Saved {path}")
    elif args.command == "baseline":
        df = eia.load(pipeline.raw_path(cfg))
        table, _ = pipeline.backtest_baselines(df, cfg["forecast"]["backtest_days"])
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(args.out)
        print(table.round(2).to_string())
        print(f"\nSaved {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
