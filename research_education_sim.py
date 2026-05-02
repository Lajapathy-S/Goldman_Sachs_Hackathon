"""
§2.5 Research, education & market data — mock catalogs and screeners only.
"""

from __future__ import annotations

import random
from typing import Any

import numpy as np
import pandas as pd

LEARNING_RESOURCES_COUNT_STORY = 600

EXPERIENCE_LEVELS = ("Getting started", "Intermediate", "Advanced")

TOPICS = (
    "Getting started",
    "Stock analysis",
    "Options strategies",
    "Retirement planning",
    "Tax planning",
    "Fundamentals",
    "Technical analysis",
)

THIRD_PARTY_PROVIDERS = [
    "Refinitiv",
    "Recognia",
    "Ned Davis Research",
    "CFRA",
    "Morningstar",
    "Zacks",
    "Argus",
    "Credit Suisse (historical)",
]


def learning_resources_catalog(
    experience: str | None = None,
    topic: str | None = None,
    n: int = 12,
    seed: int = 1,
) -> pd.DataFrame:
    rng = random.Random(seed)
    kinds = ["Article", "Video", "Webinar", "Interactive course"]
    pool: list[dict[str, Any]] = []
    for i in range(max(n * 8, 48)):
        exp = rng.choice(EXPERIENCE_LEVELS)
        top = rng.choice(TOPICS)
        pool.append(
            {
                "Title": f"{top}: lesson module {i+1} (sim)",
                "Format": rng.choice(kinds),
                "Experience": exp,
                "Topic": top,
                "Est. minutes": rng.randint(4, 45),
            }
        )
    match_all = [
        r
        for r in pool
        if (not experience or r["Experience"] == experience)
        and (not topic or r["Topic"] == topic)
    ]
    pick = match_all[:n] if len(match_all) >= n else (match_all + pool[: max(0, n - len(match_all))])[:n]
    if not pick:
        return pd.DataFrame(columns=["Title", "Format", "Experience", "Topic", "Est. minutes"])
    return pd.DataFrame(pick)


def viewpoints_weekly_issues(n: int = 5) -> list[dict[str, Any]]:
    themes = [
        "Market outlook — rates & inflation",
        "Sector spotlight — industrials",
        "Options education — collars",
        "Economic indicators dashboard",
        "International diversification",
    ]
    out = []
    for i, t in enumerate(themes[:n]):
        out.append(
            {
                "Week": f"Week {i+1} (sim)",
                "Headline": t,
                "Format": "Video + deep-dive article",
            }
        )
    return out


def aggregated_analyst_score(symbol: str) -> dict[str, Any]:
    h = sum(ord(c) for c in (symbol or "SPY").upper())
    score = 3.2 + (h % 18) / 10
    return {
        "symbol": (symbol or "SPY").upper(),
        "aggregated_score_5": round(min(5, score), 2),
        "providers_used_story": len(THIRD_PARTY_PROVIDERS),
        "note": "Single blended score — drill into provider PDFs in production.",
    }


def mock_stock_universe(n: int = 24, seed: int = 99) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    sectors = ["Tech", "Healthcare", "Financials", "Industrial", "Consumer", "Energy"]
    rows = []
    for i in range(n):
        rows.append(
            {
                "Symbol": f"SIM{i+1}",
                "Company": f"Example Co {i+1}",
                "Sector": rng.choice(sectors),
                "P/E": round(rng.uniform(8, 38), 1),
                "EPS growth %": round(rng.uniform(-5, 35), 1),
                "RSI (14)": round(rng.uniform(22, 78), 1),
                "Analyst (1–5)": round(rng.uniform(2.8, 4.6), 2),
                "ESG score": round(rng.uniform(40, 92), 0),
            }
        )
    return pd.DataFrame(rows)


def screen_stocks(
    df: pd.DataFrame,
    *,
    max_pe: float | None = None,
    min_eps_growth: float | None = None,
    max_rsi: float | None = None,
    sector: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if max_pe is not None:
        out = out[out["P/E"] <= max_pe]
    if min_eps_growth is not None:
        out = out[out["EPS growth %"] >= min_eps_growth]
    if max_rsi is not None:
        out = out[out["RSI (14)"] <= max_rsi]
    if sector and sector != "All":
        out = out[out["Sector"] == sector]
    return out.reset_index(drop=True)


def mock_etf_universe(n: int = 16, seed: int = 7) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    families = ["Fidelity", "Vanguard", "iShares", "SPDR"]
    rows = []
    for i in range(n):
        rows.append(
            {
                "Ticker": f"EX{i+1}",
                "Name": f"Broad Market ETF {i+1}",
                "Asset class": rng.choice(["US equity", "Intl equity", "Fixed income", "Balanced"]),
                "Expense %": round(rng.uniform(0.02, 0.65), 3),
                "AUM ($B)": round(rng.uniform(0.5, 120), 1),
                "Yield %": round(rng.uniform(0.8, 4.5), 2),
                "ESG": round(rng.uniform(50, 95), 0),
                "Family": rng.choice(families),
            }
        )
    return pd.DataFrame(rows)


def screen_etfs(
    df: pd.DataFrame,
    *,
    max_expense: float | None = None,
    min_yield: float | None = None,
    asset_class: str | None = None,
    family: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if max_expense is not None:
        out = out[out["Expense %"] <= max_expense]
    if min_yield is not None:
        out = out[out["Yield %"] >= min_yield]
    if asset_class and asset_class != "All":
        out = out[out["Asset class"] == asset_class]
    if family and family != "All":
        out = out[out["Family"] == family]
    return out.reset_index(drop=True)


HELP_SNIPPETS = {
    "P/E": "Price divided by earnings per share — how much investors pay per dollar of earnings (rough shortcut).",
    "RSI": "Momentum oscillator 0–100; high readings can mean strong recent gains (not a buy/sell signal by itself).",
    "Expense ratio": "Annual fund fee as a percent of assets — lower leaves more in your pocket long term.",
    "Aggregated analyst score": "Blend of multiple research shops — still read the underlying reports.",
}
