# Design decisions

A running log of choices and why they were made.

## 2026-11 — v0.1

**Separate package (`src/gridopt`) instead of notebooks.** Code that the app, the CLI and the tests all import has to live in one place. Notebooks are for exploration only.

**Baselines first.** Simple seasonal baselines are hard to beat for day-ahead load and set an honest bar. Every later model is reported next to them.

**Day-ahead framing with no look-ahead.** Forecasts for day *D* use data through the end of day *D* − 1, which matches how a battery operator would plan. All lag features are at least 24 hours old, and a test checks this.

**UTC storage, local-time features.** UTC avoids daylight-saving duplicates and gaps in the stored series; calendar features use local time because demand follows local schedules.

**Short gaps interpolated, long gaps left missing.** Filling long outages would invent data. Interpolated hours are flagged and not scored.

**Data is downloaded, not committed.** Keeps the repository small and every result reproducible from the public source.

**Region: Duke Energy Carolinas.** Local, large and growing. It is a regulated utility rather than an organized wholesale market, so there is no public hourly price; the arbitrage version (v0.2) will use public prices from a market region (PJM or ERCOT), while the Duke version can be framed as peak reduction.
