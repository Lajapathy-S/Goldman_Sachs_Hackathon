"""
Simulated Cortex / research / Gold-tier features — classroom-safe mocks only.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

MOCK_UNIVERSE: list[dict[str, Any]] = [
    {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "momentum": 0.82, "debt_to_eq": 1.5},
    {"symbol": "MSFT", "name": "Microsoft Corp.", "sector": "Technology", "momentum": 0.76, "debt_to_eq": 0.4},
    {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "momentum": 0.71, "debt_to_eq": 0.2},
    {"symbol": "XOM", "name": "Exxon Mobil", "sector": "Energy", "momentum": 0.45, "debt_to_eq": 0.35},
    {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare", "momentum": 0.55, "debt_to_eq": 0.55},
    {"symbol": "PG", "name": "Procter & Gamble", "sector": "Consumer", "momentum": 0.48, "debt_to_eq": 0.7},
    {"symbol": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology", "momentum": 0.92, "debt_to_eq": 0.6},
    {"symbol": "KO", "name": "Coca-Cola Co.", "sector": "Consumer", "momentum": 0.41, "debt_to_eq": 2.1},
]


def _seed(sym: str) -> int:
    return abs(hash(sym.upper()) + hash(date.today().isoformat())) % (2**31)


def cortex_market_digest(symbol: str) -> tuple[list[str], str]:
    """
    Three plain-language sentences mimicking an AI digest (news + technical + flow fiction).
    """
    sym = (symbol or "SPY").upper()
    s = _seed(sym)
    rng = np.random.default_rng(s)
    move = rng.choice(["rise", "dip", "sideways drift"])
    drivers = [
        "headlines about quarterly outlook",
        "sector-wide moves among peers",
        "positioning ahead of macro data",
        "technical traders reacting to short-term moving averages",
        "cross-asset flows after bond-market cues",
    ]
    d1 = rng.choice(drivers)
    d2 = rng.choice([x for x in drivers if x != d1])
    tech_note = rng.choice(
        [
            "short-term momentum oscillators turned modestly constructive",
            "price bounced near a widely watched support zone",
            "volume picked up versus its recent average",
        ]
    )
    sent1 = (
        f"{sym} is seeing a **{move}** today as investors weigh **{d1}** alongside broader market tone."
    )
    sent2 = f"On the technical side, **{tech_note}**, which some desks highlight in afternoon commentary."
    sent3 = (
        f"This digest blends **mock news themes** and **simple signals** — in production, proprietary feeds "
        f"would refresh intraday; **last simulated refresh:** **{datetime.now().strftime('%H:%M:%S')}** local."
    )
    footer = f"Simulated intraday digest · Not investment advice · Symbol **{sym}**"
    return [sent1, sent2, sent3], footer


def nl_screener_plan(query: str) -> tuple[str, dict[str, Any]]:
    """
    Map natural language to toy filters (keyword rules — not a real LLM).
    """
    q = (query or "").lower()
    filt: dict[str, Any] = {}
    notes = []

    if any(k in q for k in ("tech", "technology", "software")):
        filt["sector"] = "Technology"
        notes.append("Detected sector preference: **Technology**.")
    if any(k in q for k in ("earnings", "momentum", "growth")):
        filt["min_momentum"] = 0.65
        notes.append("Mapped **earnings / momentum** → momentum score ≥ **0.65** (mock).")
    if any(k in q for k in ("low debt", "healthy balance", "little debt")):
        filt["max_debt_to_eq"] = 0.8
        notes.append("Mapped **low debt** → debt/equity ≤ **0.8** (mock).")
    if any(k in q for k in ("energy", "oil")):
        filt["sector"] = "Energy"
        notes.append("Detected **Energy** tilt.")

    if not filt:
        filt = {"min_momentum": 0.5}
        notes.append("No strong keywords — relaxed momentum floor **0.5**.")

    plan = "**Planner (simulated):**\n" + "\n".join(f"- {n}" for n in notes)
    return plan, filt


def run_screen(filt: dict[str, Any]) -> pd.DataFrame:
    rows = []
    for r in MOCK_UNIVERSE:
        if filt.get("sector") and r["sector"] != filt["sector"]:
            continue
        if filt.get("min_momentum") is not None and r["momentum"] < filt["min_momentum"]:
            continue
        if filt.get("max_debt_to_eq") is not None and r["debt_to_eq"] > filt["max_debt_to_eq"]:
            continue
        rows.append(r)
    if not rows:
        rows = MOCK_UNIVERSE[:3]
    return pd.DataFrame(rows)


def custom_indicator_thinkscript(prompt: str) -> tuple[str, str]:
    """Pseudo–thinkscript-style output + plain explanation."""
    p = (prompt or "").lower()
    name = "CUSTOM_AI_IDX"
    if "rsi" in p:
        logic = (
            f"{name} = RSI(length = 14);\n"
            f"plot_line = {name};\n"
            f"alert_when({name} crosses_below 30 OR {name} crosses_above 70);\n"
        )
        explain = "Plots **14-period RSI** with naive crossover alerts at 30/70 for demo."
    elif "moving average" in p or "ma" in p or "cross" in p:
        logic = (
            f"slowMA = Average(close, 50);\nfastMA = Average(close, 20);\n"
            f"plot(slowMA); plot(fastMA);\n"
            f"signal = CrossesAbove(fastMA, slowMA);\n"
        )
        explain = "**Fast MA vs slow MA** cross idea — classic teaching pattern."
    else:
        logic = (
            f"{name} = (close - Lowest(low, 20)) / (Highest(high, 20) - Lowest(low, 20)) * 100;\n"
            f"plot({name});\n"
        )
        explain = "Defaulted to a **20-period stochastic-style** oscillator bounded 0–100."

    return logic, explain


def morningstar_premium_mock(symbol: str) -> dict[str, Any]:
    sym = (symbol or "AAPL").upper()
    h = _seed(sym)
    ratings = ["Buy", "Hold", "Sell"]
    moats = ["Wide", "Narrow", "None"]
    unc = ["Low", "Medium", "High"]
    return {
        "symbol": sym,
        "analyst_rating": ratings[h % 3],
        "fair_value_estimate": round(120 + (h % 200) + (h % 50) * 0.1, 2),
        "current_mock_price": round(80 + (h % 150), 2),
        "uncertainty_rating": unc[h % 3],
        "economic_moat": moats[h % 3],
        "report_blurb": (
            f"Morningstar-style narrative (mock): **{sym}** balances cyclical revenue streams "
            f"with balance-sheet flexibility; valuation hinges on terminal growth assumptions."
        ),
    }


def nasdaq_level2_mock(symbol: str, levels: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    sym = (symbol or "SPY").upper()
    rng = np.random.default_rng(_seed(sym))
    mid = 400 + (rng.random() * 50)
    spread = 0.02
    bids = []
    asks = []
    for i in range(levels):
        bp = mid - spread / 2 - i * 0.01
        ap = mid + spread / 2 + i * 0.01
        bids.append({"price": round(bp, 2), "size": int(rng.integers(100, 9000))})
        asks.append({"price": round(ap, 2), "size": int(rng.integers(100, 9000))})
    return pd.DataFrame(bids), pd.DataFrame(asks)


def earnings_calendar_rows(tickers: list[str]) -> pd.DataFrame:
    rows = []
    for t in tickers:
        if not t:
            continue
        h = _seed(t.strip())
        rng = np.random.default_rng(h)
        d = date.today() + timedelta(days=int(rng.integers(5, 90)))
        eps_est = round(rng.uniform(0.5, 6.0), 2)
        rows.append(
            {
                "symbol": t.strip().upper(),
                "report_date": d.isoformat(),
                "eps_estimate_mock": eps_est,
                "session": rng.choice(["After close", "Before open"]),
            }
        )
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def personalized_news_lines(tickers: list[str], n: int = 8) -> list[dict[str, str]]:
    sources = ["Reuters (mock)", "AP (mock)", "Bloomberg excerpt (mock)", "Editorial (mock)"]
    lines = []
    tickers = [t for t in tickers if t][:6]
    if not tickers:
        tickers = ["SPY", "QQQ"]
    for i in range(n):
        t = tickers[i % len(tickers)].upper()
        lines.append(
            {
                "headline": f"{t}: markets digest regulatory chatter — simulated headline {i+1}",
                "source": sources[i % len(sources)],
                "time": datetime.now().strftime("%H:%M"),
            }
        )
    return lines


def post_earnings_reaction(symbol: str) -> dict[str, Any]:
    rng = np.random.default_rng(_seed(symbol))
    return {
        "symbol": symbol.upper(),
        "price_change_pct_mock": round(rng.uniform(-6, 8), 2),
        "volume_vs_avg": round(rng.uniform(0.8, 2.2), 2),
        "comment": "Illustrative post-earnings move — not historical data.",
    }
