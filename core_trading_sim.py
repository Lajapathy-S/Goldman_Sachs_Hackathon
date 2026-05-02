"""
§3.1 Core trading features — pricing stories and illustrative calculators (simulation only).
"""

from __future__ import annotations

import random
from typing import Any

COMMISSION_US_STOCK_ETF = 0.0
OPTION_FEE_PER_CONTRACT = 0.65
NO_ACCOUNT_MINIMUM = True
NO_INACTIVITY_FEE = True
NO_MAINTENANCE_FEE = True

BOND_INVENTORY_STORY = 50_000
FOREX_PAIRS_STORY = 60
STOCK_SLICE_MIN_USD = 5.0
STOCK_SLICES_MAX_NAMES = 30

SP500_SAMPLE_TICKERS = (
    "AAPL MSFT AMZN NVDA GOOGL META TSLA BRK.B UNH JNJ XOM JPM V PG MA HD CVX MRK "
    "ABBV PEP KO COST TMO WFC ACN DIS MCD CSCO LIN PM TXN QCOM HON UPS BA IBM AMAT "
    "NEE SPGI LOW INTU ISRG BKNG DE ADP TJX SYK CL MDLZ CB CI MMC"
).split()


def commission_schedule_summary() -> dict[str, Any]:
    return {
        "us_stock_etf_commission": COMMISSION_US_STOCK_ETF,
        "options_per_contract": OPTION_FEE_PER_CONTRACT,
        "account_minimum": 0 if NO_ACCOUNT_MINIMUM else None,
        "inactivity_fee": NO_INACTIVITY_FEE,
        "maintenance_fee": NO_MAINTENANCE_FEE,
        "note": "Online US stock & ETF trades — $0 commission story; options +$0.65/contract (sim).",
    }


def estimate_options_commission(contracts: float, legs: int = 1) -> dict[str, Any]:
    c = max(0.0, float(contracts))
    legs_n = max(1, int(legs))
    fee = c * legs_n * OPTION_FEE_PER_CONTRACT
    return {
        "contracts_per_leg": c,
        "legs": legs_n,
        "estimated_commission": round(fee, 2),
        "display": f"${fee:,.2f} at ${OPTION_FEE_PER_CONTRACT}/contract/leg (story)",
    }


def validate_stock_slices(lines: list[tuple[str, float]]) -> dict[str, Any]:
    """
    lines: (ticker, dollar_amount) for S&P 500 «Stock Slices» story.
    """
    errs: list[str] = []
    if len(lines) > STOCK_SLICES_MAX_NAMES:
        errs.append(f"Max **{STOCK_SLICES_MAX_NAMES}** names per basket order (story).")
    total = 0.0
    for sym, amt in lines:
        if amt < STOCK_SLICE_MIN_USD - 1e-9:
            errs.append(f"{sym}: minimum **${STOCK_SLICE_MIN_USD:g}** per slice (story).")
        total += amt
    return {
        "valid": len(errs) == 0,
        "line_count": len(lines),
        "notional_total": round(total, 2),
        "errors": errs,
        "commission": COMMISSION_US_STOCK_ETF,
    }


def walk_limit_story(mid: float, bid: float, ask: float, aggression: float = 0.35) -> dict[str, Any]:
    """
    Walk Limit® — nudge limit toward mid without lifting through spread (illustrative).
    aggression 0..1 moves from passive bid toward mid.
    """
    spread = max(1e-6, ask - bid)
    passive = bid + spread * 0.05
    target = bid + spread * min(0.85, max(0.1, aggression))
    improvement_vs_passive = target - passive
    return {
        "reference_mid": round(mid, 4),
        "bid": round(bid, 4),
        "ask": round(ask, 4),
        "spread": round(spread, 6),
        "passive_limit_story": round(passive, 4),
        "walk_limit_adjusted_story": round(target, 4),
        "ticks_improved_story": round(improvement_vs_passive / spread * 10, 1),
        "note": "thinkorswim Walk Limit® adjusts working limits over time to seek fills — sim math only.",
    }


def futures_universe_story() -> dict[str, Any]:
    return {
        "complex": "thinkorswim — equity index, energy, metals, agriculture, currencies, interest rates",
        "hours_equity_index_story": "Nearly 24/5 on futures platform (story)",
        "crypto_futures_hours_story": "Crypto futures often quoted 24/7 where listed (story)",
        "disclaimer": "Futures are leveraged — not suitable for all investors.",
    }


def forex_panel_story(base_spread_pips: float = 1.2) -> dict[str, Any]:
    pairs = [
        "EUR/USD",
        "USD/JPY",
        "GBP/USD",
        "USD/CHF",
        "AUD/USD",
        "USD/CAD",
        "NZD/USD",
        "EUR/GBP",
    ]
    return {
        "pairs_available_story": f"{FOREX_PAIRS_STORY}+",
        "pricing": "Spread-based — no minimum lot size story on retail FX at platform",
        "hours": "24/5 Sun evening–Fri (story)",
        "sample_spread_pips": base_spread_pips,
        "sample_watchlist": pairs,
    }


def mock_bondsource_rows(n: int = 10, seed: int = 11) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    kinds = ["Corporate", "Municipal", "Treasury", "Agency", "CD"]
    rows = []
    for i in range(n):
        bid = round(rng.uniform(97.5, 102.5), 3)
        spr = rng.uniform(0.02, 0.35)
        ask = round(bid + spr, 3)
        rows.append(
            {
                "CUSIP (sim)": f"{10000000 + i}",
                "Type": rng.choice(kinds),
                "Coupon %": round(rng.uniform(2.0, 6.5), 2),
                "Maturity": f"{2027 + rng.randint(0, 18)}",
                "Bid": bid,
                "Ask": ask,
                "YTM bid/ask (sim)": f"{rng.uniform(4.0, 6.5):.2f}% / {rng.uniform(4.0, 6.5):.2f}%",
            }
        )
    return rows


def fixed_income_story_box() -> dict[str, Any]:
    return {
        "inventory_story": f"{BOND_INVENTORY_STORY:,}+ secondary offerings",
        "bondsource": "BondSource™ — consolidated inventory with bid/ask transparency (story)",
        "treasury_auctions": "Participate in Treasury auctions where offered — calendar in platform (story)",
        "cds": "Brokered CDs — competitive rates vs bank branches (story)",
    }
