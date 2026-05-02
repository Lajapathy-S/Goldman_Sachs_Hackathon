"""
Schwab research, education & screeners — simulation only.
"""

from __future__ import annotations

import random
from typing import Any

import numpy as np
import pandas as pd

EQUITY_RATINGS_UNIVERSE_STORY = 3_000

THIRD_PARTY_PROVIDERS = [
    "Credit Suisse",
    "Argus",
    "CFRA",
    "Morningstar",
    "Market Edge",
    "Ned Davis Research",
    "Zacks",
    "William Blair",
    "S&P Capital IQ",
    "Jaywalk Consensus",
    "Research Team Alpha (story)",
]

SCHWAB_LEARNING_TOPICS = (
    "Beginner investing",
    "Options",
    "Fixed income",
    "ETFs",
    "Market analysis",
    "Tax-smart investing",
)

LEARNING_FORMATS = ("Articles", "Videos", "Webinars", "Courses")


def schwab_equity_ratings_story() -> dict[str, Any]:
    return {
        "product": "Schwab Equity Ratings®",
        "scale": "Proprietary **A through F** grades for **US equities** — quantitative factor model (story)",
        "coverage": f"Ratings for **{EQUITY_RATINGS_UNIVERSE_STORY:,}+** symbols refreshed **weekly** (story)",
        "access": "**Free** to Schwab brokerage clients — quote / research pages & stock screener column",
    }


def mock_equity_ratings_sample(seed: int = 51) -> pd.DataFrame:
    rng = random.Random(seed)
    syms = ["AAPL", "MSFT", "JPM", "XOM", "UNH", "HD", "CAT", "DIS"]
    grades = list("ABCDEF")
    rows = []
    for s in syms:
        rows.append(
            {
                "Symbol": s,
                "Schwab Equity Rating®": rng.choice(grades[:5]),
                "Factor tilt (sim)": rng.choice(["Quality", "Value", "Momentum blend"]),
            }
        )
    return pd.DataFrame(rows)


def third_party_research_story() -> dict[str, Any]:
    n = len(THIRD_PARTY_PROVIDERS)
    return {
        "suite": "Third-Party Research",
        "providers_story": f"**{n}+** providers in narrative — examples: "
        + ", ".join(THIRD_PARTY_PROVIDERS[:8])
        + ", …",
        "experience": "Aggregated **single equity research hub** per ticker — jump to each provider PDF/HTML report",
        "disclaimer": "Third-party opinions independent of Schwab — read disclosures on each report.",
    }


def daily_market_commentary_audio_story() -> dict[str, Any]:
    return {
        "product": "Daily Market Commentary (Audio)",
        "format": "**5–10 minute** desk commentary covering macro + sector themes (story)",
        "channels": ["Schwab **Mobile** app podcast/stream", "**Alexa** skill — voice playback"],
        "cadence": "Publish trading-day wrap — archive searchable by date (story)",
    }


def schwab_learning_center_story() -> dict[str, Any]:
    return {
        "center": "Schwab Learning Center",
        "taxonomy": f"Topics: **{', '.join(SCHWAB_LEARNING_TOPICS)}** — formats: **{', '.join(LEARNING_FORMATS)}**",
        "integration": "Cross-links with **Schwab Coaching®** modules surfaced inside **thinkorswim®** education drawer (story)",
    }


def mock_stock_universe_schwab(n: int = 24, seed: int = 63) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        rows.append(
            {
                "Symbol": f"SX{i+1}",
                "Market cap ($B)": round(rng.uniform(2, 900), 1),
                "P/E": round(rng.uniform(10, 42), 1),
                "EPS growth %": round(rng.uniform(-8, 28), 1),
                "Dividend yield %": round(rng.uniform(0, 4.5), 2),
                "RSI (14)": round(rng.uniform(28, 72), 1),
                "Schwab Equity Rating®": rng.choice(["A", "B", "C", "D"]),
            }
        )
    return pd.DataFrame(rows)


def screen_stocks_schwab(
    df: pd.DataFrame,
    *,
    max_pe: float | None = None,
    min_div_yield: float | None = None,
    min_rating_letter: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if max_pe is not None:
        out = out[out["P/E"] <= max_pe]
    if min_div_yield is not None:
        out = out[out["Dividend yield %"] >= min_div_yield]
    order = {"A": 5, "B": 4, "C": 3, "D": 2, "F": 1}
    if min_rating_letter and "Schwab Equity Rating®" in out.columns:
        floor = order.get(min_rating_letter.upper(), 3)
        out = out[out["Schwab Equity Rating®"].map(lambda x: order.get(str(x), 0)) >= floor]
    return out.reset_index(drop=True)


def mock_etf_universe_schwab(n: int = 18, seed: int = 71) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cats = ["US equity", "Intl equity", "Sector", "Bond", "Balanced", "Commodity"]
    issuers = ["Schwab", "iShares", "Vanguard", "SPDR"]
    rows = []
    for i in range(n):
        rows.append(
            {
                "Ticker": f"EZ{i+1}",
                "Category": rng.choice(cats),
                "Expense %": round(rng.uniform(0.03, 0.55), 3),
                "Yield %": round(rng.uniform(0.5, 4.2), 2),
                "AUM ($B)": round(rng.uniform(0.2, 90), 1),
                "10yr ret % (sim)": round(rng.uniform(4, 14), 1),
                "Issuer": rng.choice(issuers),
                "ESG score": round(rng.uniform(55, 92), 0),
            }
        )
    return pd.DataFrame(rows)


def screen_etfs_schwab(
    df: pd.DataFrame,
    *,
    max_expense: float | None = None,
    min_yield: float | None = None,
    issuer: str | None = None,
    category: str | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if max_expense is not None:
        out = out[out["Expense %"] <= max_expense]
    if min_yield is not None:
        out = out[out["Yield %"] >= min_yield]
    if issuer and issuer != "All":
        out = out[out["Issuer"] == issuer]
    if category and category != "All":
        out = out[out["Category"] == category]
    return out.reset_index(drop=True)


def mock_option_contracts_screen(seed: int = 88) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(12):
        strike = round(rng.uniform(150, 520), 2)
        rows.append(
            {
                "Underlying": rng.choice(["SPY", "QQQ", "IWM", "AAPL"]),
                "Expiry": "2026-06-19",
                "Strike": strike,
                "Type": rng.choice(["Call", "Put"]),
                "IV %": round(rng.uniform(14, 42), 1),
                "IV percentile": round(rng.uniform(15, 95), 0),
                "Volume": int(rng.integers(50, 50000)),
                "OI": int(rng.integers(100, 200000)),
                "Delta (sim)": round(rng.uniform(-0.55, 0.55), 2),
            }
        )
    return pd.DataFrame(rows)


def filter_options_chain(
    df: pd.DataFrame,
    *,
    min_iv_pct: float | None = None,
    min_volume: int | None = None,
) -> pd.DataFrame:
    out = df.copy()
    if min_iv_pct is not None:
        out = out[out["IV %"] >= min_iv_pct]
    if min_volume is not None:
        out = out[out["Volume"] >= min_volume]
    return out.reset_index(drop=True)


def economic_calendar_rows(n: int = 8, seed: int = 99) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    events = [
        ("CPI m/m", "8:30 ET", "0.2% cons.", "0.1% prior"),
        ("FOMC decision", "2:00 ET", "5.25–5.50%", "—"),
        ("Nonfarm payrolls", "8:30 ET", "180k", "175k prior"),
        ("GDP advance", "8:30 ET", "2.1% annualized", "2.0% prior"),
        ("PCE deflator", "8:30 ET", "0.2% m/m", "0.1% prior"),
    ]
    rows = []
    for i in range(n):
        name, t, cons, prior = rng.choice(events)
        day = 5 + (i * 2) % 20
        month = 1 + (i % 3)
        rows.append(
            {
                "Date (sim)": f"2026-{month:02d}-{day:02d}",
                "Event": name,
                "Time": t,
                "Consensus (sim)": cons,
                "Prior / last (sim)": prior,
                "Reaction data": "Intraday % move on SPY (sim) " + str(round(rng.uniform(-0.8, 0.8), 2)) + "%",
            }
        )
    return rows


def fixed_income_bondsource_story() -> dict[str, Any]:
    return {
        "platform": "BondSource™ — Fixed Income Research",
        "inventory": "Real-time **secondary** bond inventory — transparent bid/ask (story)",
        "trace": "**TRACE** transaction prints integrated where available — liquidity caveats",
        "screener": "**50+** filter dimensions — coupon, maturity ladder, yield/YTW, credit tier (story)",
        "education": "Issuer tear sheets & scenario yields — still verify suitability",
    }


def mock_bond_screener_rows(n: int = 10, seed: int = 17) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    kinds = ["Corporate IG", "Agency", "Municipal", "Treasury"]
    rows = []
    for i in range(n):
        rows.append(
            {
                "CUSIP (sim)": f"91282{i:03d}",
                "Issuer type": rng.choice(kinds),
                "Coupon %": round(rng.uniform(2.5, 6.0), 2),
                "YTW %": round(rng.uniform(4.2, 6.8), 2),
                "Maturity": f"{2028 + rng.integers(0, 8)}",
                "Bid": round(rng.uniform(98, 102), 3),
                "Ask": round(rng.uniform(98.2, 102.5), 3),
            }
        )
    return pd.DataFrame(rows)


def unusual_options_activity_story() -> dict[str, Any]:
    return {
        "alert_type": "Unusual options activity",
        "signals": ["Volume vs OI spike", "Sweep vs floor prints", "Opening vs closing notionals"],
        "delivery": "Scanner tile + optional push when thresholds breach (story)",
    }


def analyst_ratings_equity_research_story() -> dict[str, Any]:
    return {
        "product": "Analyst Ratings (Equity Research)",
        "summary_bar": "Aggregated **Buy / Outperform / Hold / Underperform / Sell** counts with **consensus** label",
        "price_target": "Mean & median **12-mo price target** — high/low range strip chart on desktop (story)",
        "drill_down": "Filter to **individual analysts** — firm, prior rating, **hit rate / track record** where disclosed",
        "refresh": "Consensus updates as contributing brokers revise — latency varies by vendor feed",
    }


def mock_analyst_consensus(symbol: str, seed: int = 33) -> dict[str, Any]:
    rng = random.Random(seed + sum(ord(c) for c in symbol.upper()))
    buy = rng.randint(8, 22)
    hold = rng.randint(5, 14)
    sell = max(0, rng.randint(0, 4))
    pt = round(rng.uniform(140, 520), 2)
    return {
        "symbol": symbol.upper(),
        "consensus_label_story": rng.choice(["Buy", "Outperform", "Hold"]),
        "buy": buy,
        "hold": hold,
        "sell": sell,
        "mean_price_target": pt,
        "median_price_target": round(pt * rng.uniform(0.96, 1.04), 2),
        "contributors_story": buy + hold + sell,
    }


def mock_individual_analyst_ratings(symbol: str, n: int = 6, seed: int = 44) -> pd.DataFrame:
    rng = np.random.default_rng(seed + len(symbol))
    firms = ["Northstar Research", "Harbor Securities", "Summit Equity", "Meridian Analytics", "Coastal Capital"]
    rows = []
    for i in range(n):
        rows.append(
            {
                "Firm (sim)": firms[i % len(firms)],
                "Analyst (sim)": f"Analyst {chr(65 + i)}",
                "Rating": rng.choice(["Buy", "Hold", "Sell"]),
                "Price target": round(rng.uniform(130, 540), 2),
                "Prior rating": rng.choice(["Buy", "Hold", "Sell"]),
                "Track record % (sim)": round(rng.uniform(52, 71), 0),
            }
        )
    return pd.DataFrame(rows)


def schwab_network_live_tv_story() -> dict[str, Any]:
    return {
        "product": "Schwab Network (Live Financial TV)",
        "programming": "**Live** financial news, **market analysis**, and **educational** segments (story)",
        "distribution": "Stream via **Schwab Mobile** app and **schwab.com** — desktop player + casting options",
        "talent": "Real-time commentary from **traders & analysts** — ticker-linked segments during market hours",
        "schedule": "Full-day grid + on-demand clips — advertising disclosures where applicable",
    }


def market_snapshot_alerts_story() -> dict[str, Any]:
    return {
        "product": "Schwab Market Snapshot Alerts",
        "trigger_types": [
            "**Index** level crosses / % moves (SPX, COMP, etc.)",
            "**Volatility** spikes — VIX thresholds",
            "**Economic data** prints vs consensus",
            "Sector breadth / earnings headlines (where wired)",
        ],
        "channels": ["Push notification", "Email", "SMS"],
        "customization": "Per-symbol & index thresholds — quiet hours & batching settings (story)",
    }


def mock_alert_presets() -> list[dict[str, str]]:
    return [
        {"Alert name (sim)": "SPX crosses 6,000", "Channel": "Push + Email"},
        {"Alert name (sim)": "VIX above 22", "Channel": "SMS"},
        {"Alert name (sim)": "CPI surprise vs consensus", "Channel": "Push"},
        {"Alert name (sim)": "QQQ down 1.5% from prior close", "Channel": "Email"},
    ]
