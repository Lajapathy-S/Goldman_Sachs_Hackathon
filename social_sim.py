"""
Social / community / gamification — mock feeds only; no real users or trades.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from typing import Any

import pandas as pd

LAUNCH_STORY = "Robinhood Social — embedded community (launch story **2026**)"


MOCK_TRADERS = [
    {"handle": "@index_pat", "followers_k": 42, "ytd_return_pct": 11.2, "badge": "Educational"},
    {"handle": "@div_diamond", "followers_k": 128, "ytd_return_pct": 6.8, "badge": "Income"},
    {"handle": "@macro_maya", "followers_k": 89, "ytd_return_pct": -2.1, "badge": "Macro"},
]


def live_trade_feed(seed: int = 7, n: int = 8) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    syms = ["SPY", "QQQ", "AAPL", "TSLA", "NVDA", "VTI", "MSFT", "GOOGL"]
    sides = ["BUY", "SELL"]
    out = []
    for i in range(n):
        sym = rng.choice(syms)
        out.append(
            {
                "time": (datetime.now() - timedelta(minutes=rng.randint(1, 120))).strftime("%H:%M"),
                "trader": rng.choice([t["handle"] for t in MOCK_TRADERS]),
                "side": rng.choice(sides),
                "symbol": sym,
                "note": rng.choice(
                    [
                        "Adds to core sleeve",
                        "Trim risk before CPI",
                        "Idea only — not advice",
                    ]
                ),
            }
        )
    return out


def discussion_teasers() -> list[str]:
    return [
        "**Ideas channel:** Are mega-cap valuations stretched vs earnings?",
        "**Strategies:** Dollar-cost averaging vs lump-sum — friendly debate.",
        "**Risk reminder:** Past chats ≠ future returns.",
    ]


def tipranks_style_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    politicians = pd.DataFrame(
        [
            {"name": "Sen. Example (sim)", "symbol": "DEF", "activity": "Sold · disclosure lag mock"},
            {"name": "Rep. Sample (sim)", "symbol": "ABC", "activity": "Bought · teaching row"},
        ]
    )
    hedge = pd.DataFrame(
        [
            {"fund": "Alpha Macro LP (sim)", "symbol": "GLD", "change_pct_display": "+1.2% q/q"},
            {"fund": "Beta Value (sim)", "symbol": "XOM", "change_pct_display": "-0.4% q/q"},
        ]
    )
    insiders = pd.DataFrame(
        [
            {"company": "Example Co. (sim)", "symbol": "EXM", "insider": "CFO", "type": "Purchase"},
            {"company": "Sample Tech (sim)", "symbol": "SMP", "insider": "Director", "type": "Sale"},
        ]
    )
    return politicians, hedge, insiders


def referral_reward_story() -> dict[str, str]:
    return {
        "referrer": "Random **free stock** slice (~$5–$25 notional story) when referee funds.",
        "referee": "Welcome **free stock** after first deposit clears.",
        "fine_print": "Rewards simulated — real programs have eligibility rules & taxes.",
    }


def free_stock_value_band() -> tuple[float, float]:
    return 5.0, 25.0

