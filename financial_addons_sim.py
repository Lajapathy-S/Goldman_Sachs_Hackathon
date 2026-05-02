"""
Mutual fund screener, options ideas, earnings calendar, credit score — simulation only.
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import pandas as pd

MUTUAL_FUNDS_COUNT_STORY = 10_000

LOAD_TYPES = ("No-load", "Front-load", "Deferred")


def mock_mutual_fund_universe(n: int = 48, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    cats = [
        "Large blend",
        "Large growth",
        "Large value",
        "International",
        "Bond intermediate",
        "Target-date 2040",
    ]
    rows = []
    for i in range(n):
        is_zero = i % 7 == 0 and i > 0
        sym = f"FZ{i:03d}" if is_zero else f"MF{i+1:04d}"
        exp = 0.0 if is_zero else round(rng.uniform(0.03, 1.15), 3)
        rows.append(
            {
                "Symbol": sym,
                "Name": ("Fidelity ZERO " if is_zero else "Sample ") + f"Index Fund {i+1}",
                "Morningstar": int(rng.integers(3, 6)),
                "Expense %": exp,
                "Load": rng.choice(list(LOAD_TYPES)),
                "Manager tenure (yrs)": round(rng.uniform(1.0, 22.0), 1),
                "Category": rng.choice(cats),
                "Min investment ($)": int(rng.choice([0, 500, 2500, 10000, 50000])),
                "Fidelity ZERO": "Yes" if is_zero else "",
            }
        )
    return pd.DataFrame(rows)


def screen_mutual_funds(
    df: pd.DataFrame,
    *,
    min_morningstar: int | None = None,
    max_expense: float | None = None,
    load_pref: str | None = None,
    min_manager_tenure: float | None = None,
    category: str | None = None,
    max_min_investment: float | None = None,
    zero_only: bool = False,
) -> pd.DataFrame:
    out = df.copy()
    if min_morningstar is not None:
        out = out[out["Morningstar"] >= min_morningstar]
    if max_expense is not None:
        out = out[out["Expense %"] <= max_expense]
    if load_pref and load_pref != "Any":
        out = out[out["Load"] == load_pref]
    if min_manager_tenure is not None:
        out = out[out["Manager tenure (yrs)"] >= min_manager_tenure]
    if category and category != "All":
        out = out[out["Category"] == category]
    if max_min_investment is not None:
        out = out[out["Min investment ($)"] <= max_min_investment]
    if zero_only:
        out = out[out["Fidelity ZERO"] == "Yes"]
    return out.reset_index(drop=True)


def options_idea_bundle(outlook: str, risk: str) -> dict[str, Any]:
    """Plain-language outcomes first, then named strategies (sim)."""
    o = outlook.strip().lower()
    r = risk.strip().lower()
    intro = (
        "Below is a **simplified** illustration. Real options involve assignment risk, "
        "multi-leg fees, and tax nuance — not advice."
    )
    if o == "bullish":
        outlook_plain = (
            "You expect the stock or index to rise or stay firm. Risk/reward tilts toward "
            "participating in upside; hedges often cost premium."
        )
    elif o == "bearish":
        outlook_plain = (
            "You expect prices to fall or volatility to hurt long stock. Strategies may cap "
            "downside or profit from a drop but often trade away upside or involve timing risk."
        )
    else:
        outlook_plain = (
            "You expect a range-bound market — smaller moves, possible chop. Income-style "
            "trades can collect premium but may lose if a large breakout happens."
        )

    if "conservative" in r:
        risk_plain = "You prefer defined risk and smaller net premium outlay when possible."
        tier = "conservative"
    elif "aggressive" in r or "high" in r:
        risk_plain = "You accept larger swings for potentially higher payoff or leverage-like profiles."
        tier = "aggressive"
    else:
        risk_plain = "You balance premium collected vs. tail scenarios."
        tier = "moderate"

    key = f"{o}|{tier}"
    strategies: list[dict[str, str]] = {
        "bullish|conservative": [
            {
                "Strategy": "Covered call (stock + short call)",
                "What you might see (plain language)": (
                    "You keep shares unless assigned above the strike; premium reduces cost basis "
                    "but caps upside above that strike."
                ),
                "Sketch": "Long stock, short OTM call — income bias, defined upside cap.",
            },
            {
                "Strategy": "Cash-secured put",
                "What you might see (plain language)": (
                    "You earn premium now; if assigned, you buy stock at the strike (cash set aside)."
                ),
                "Sketch": "Short put secured by cash — entry discount story.",
            },
        ],
        "bullish|moderate": [
            {
                "Strategy": "Bull call spread",
                "What you might see (plain language)": (
                    "Cheaper than stock alone for directional upside to a cap — max loss is the debit paid."
                ),
                "Sketch": "Long call lower strike, short call higher strike.",
            },
        ],
        "bullish|aggressive": [
            {
                "Strategy": "Long calls / LEAPS",
                "What you might see (plain language)": (
                    "Large upside if you're right; time decay hurts if the move is slow."
                ),
                "Sketch": "Long option — convex payoff, theta drag.",
            },
        ],
        "bearish|conservative": [
            {
                "Strategy": "Protective put",
                "What you might see (plain language)": (
                    "You pay premium for a floor on stock — like insurance for a period."
                ),
                "Sketch": "Long stock + long put.",
            },
        ],
        "bearish|moderate": [
            {
                "Strategy": "Bear put spread",
                "What you might see (plain language)": (
                    "Defined-risk bearish bet — profits if price falls into the spread window."
                ),
                "Sketch": "Long put higher strike, short put lower strike.",
            },
        ],
        "bearish|aggressive": [
            {
                "Strategy": "Long puts",
                "What you might see (plain language)": (
                    "Direct downside exposure; decay hurts sideways grind."
                ),
                "Sketch": "Long put — negative delta.",
            },
        ],
        "neutral|conservative": [
            {
                "Strategy": "Iron condor (wide)",
                "What you might see (plain language)": (
                    "Collect premium if price stays in a range; tail moves can hurt quickly."
                ),
                "Sketch": "OTM call spread + OTM put spread.",
            },
        ],
        "neutral|moderate": [
            {
                "Strategy": "Short strangle / straddle (advanced)",
                "What you might see (plain language)": (
                    "Income if calm; large losses possible if the market breaks hard either way."
                ),
                "Sketch": "Short call + short put — undefined risk unless hedged.",
            },
        ],
        "neutral|aggressive": [
            {
                "Strategy": "Calendar spread",
                "What you might see (plain language)": (
                    "Bet on volatility or timing differences between expirations — complexity up."
                ),
                "Sketch": "Same strike, different expirations.",
            },
        ],
    }.get(
        key,
        [
            {
                "Strategy": "Long stock / index ETF",
                "What you might see (plain language)": (
                    "Simple exposure — full upside and downside of the shares."
                ),
                "Sketch": "Baseline for comparing option overlays.",
            }
        ],
    )

    return {
        "disclaimer": intro,
        "outlook_summary": outlook_plain,
        "risk_posture": risk_plain,
        "strategies": strategies,
    }


def _sym_seed(sym: str) -> int:
    return int(hashlib.sha256(sym.upper().encode()).hexdigest()[:8], 16)


def earnings_rows_for_symbols(symbols: list[str]) -> pd.DataFrame:
    rows = []
    for sym in symbols:
        s = (sym or "").strip().upper()
        if not s:
            continue
        rng = np.random.default_rng(_sym_seed(s))
        days_ahead = int(rng.integers(2, 45))
        prev_beat = rng.random() > 0.35
        rows.append(
            {
                "Symbol": s,
                "Earnings date (sim)": f"In ~{days_ahead} trading days",
                "EPS estimate (sim)": round(rng.uniform(0.5, 4.5), 2),
                "Prior quarter EPS (sim)": round(rng.uniform(0.4, 4.2), 2),
                "Prior result vs est. (sim)": "Beat" if prev_beat else "Miss",
            }
        )
    if not rows:
        return pd.DataFrame(
            columns=[
                "Symbol",
                "Earnings date (sim)",
                "EPS estimate (sim)",
                "Prior quarter EPS (sim)",
                "Prior result vs est. (sim)",
            ]
        )
    return pd.DataFrame(rows)


def credit_score_snapshot(seed_user: str = "demo") -> dict[str, Any]:
    rng = np.random.default_rng(int(hashlib.md5(seed_user.encode()).hexdigest()[:8], 16) % (2**31))
    score = int(rng.integers(680, 790))
    bureau = rng.choice(["Experian", "Equifax"])
    past = int(np.clip(score - int(rng.integers(25, 85)), 620, 820))
    series = [past]
    for _ in range(4):
        series.append(int(np.clip(series[-1] + int(rng.integers(-12, 18)), 620, 820)))
    series.append(score)
    labels = ["M-5", "M-4", "M-3", "M-2", "M-1", "Current"]
    months = [{"Month": labels[i], "Score (sim)": series[i]} for i in range(6)]
    tips = [
        "Pay down revolving balances below ~30% of limits.",
        "Keep old accounts open if there's no annual fee — age helps.",
        "Dispute errors promptly; one wrong late mark can drag the score.",
        "Space out new credit applications — hard pulls add noise.",
    ]
    return {
        "bureau_story": bureau,
        "current_score_vantage_like": score,
        "monthly_history_sim": months,
        "tips": tips,
        "note": "Simulated score — production shows a soft/informational pull with no hard inquiry for viewing.",
    }
