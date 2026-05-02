"""
Fidelity-style brokerage stories — educational mocks only, not Fidelity services.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

US_STOCK_ETF_COMMISSION_ONLINE = 0.0
MINIMUM_OPEN_BALANCE_USD = 0.0

INTL_COMMISSION_NOTES = [
    {"market": "UK (LSE)", "schedule": "Illustrative % of trade notional or flat — check live schedule."},
    {"market": "Canada (TSX)", "schedule": "CAD-denominated; FX spread may apply."},
    {"market": "Japan (TSE)", "schedule": "JPY pricing; session fees may apply."},
    {"market": "Hong Kong", "schedule": "HKD; stamp duty story in disclosures."},
    {"market": "Germany (XETRA)", "schedule": "EUR; exchange fees separate."},
]

OPTIONS_CONTRACT_FEE_USD = 0.65

MULTI_LEG_STRATEGIES = [
    "Vertical / calendar spreads",
    "Straddles & strangles",
    "Iron condors",
    "Butterflies",
    "Cash-secured puts / covered calls",
]

SLICE_MIN_USD = 1.0
SLICE_UNIVERSE_NOTE = "S&P 500 constituents (story: Stocks by the Slice™-style)"

ZERO_EXPENSE_FUNDS = ["FZROX", "FZILX", "FNILX"]
NTF_FUNDS_COUNT_ILLUSTRATIVE = 3300
TOTAL_FUNDS_ACCESS_ILLUSTRATIVE = 10_000

MARGIN_BASE_RATE_ANNUAL = 0.1057
MARGIN_PREMIUM_TIER_RATE = 0.075
MARGIN_PREMIUM_TIER_BALANCE_USD = 1_000_000

FOREX_PAIRS = [
    "EUR/USD",
    "USD/JPY",
    "GBP/USD",
    "AUD/USD",
    "USD/CAD",
    "USD/CHF",
    "NZD/USD",
    "EUR/GBP",
    "EUR/JPY",
    "GBP/JPY",
    "AUD/JPY",
    "EUR/AUD",
    "USD/MXN",
    "USD/CNH",
    "USD/SGD",
    "USD/HKD",
    "USD/ZAR",
]

INTERNATIONAL_MARKETS = [
    "United Kingdom",
    "Canada",
    "Japan",
    "Hong Kong",
    "Germany",
    "France",
    "Switzerland",
    "Australia",
    "Italy",
    "Spain",
    "Netherlands",
    "Sweden",
    "Norway",
    "Denmark",
    "Belgium",
    "Singapore",
    "South Korea",
    "Taiwan",
    "Mexico",
    "Brazil",
    "India",
    "South Africa",
    "Israel",
    "New Zealand",
    "Ireland",
    "Finland",
]

EXTENDED_PRE_MARKET = "7:00 AM–9:30 AM ET"
EXTENDED_AFTER_HOURS = "4:00 PM–8:00 PM ET"


def fractional_slice_from_dollars(dollars: float, reference_price: float) -> dict[str, Any]:
    d = max(SLICE_MIN_USD, float(dollars))
    if reference_price <= 0:
        return {"error": "Need a positive reference price."}
    return {
        "dollars": d,
        "approx_shares": d / reference_price,
        "min_order_usd": SLICE_MIN_USD,
        "note": "Fractional shares display beside whole shares in portfolio views (simulation).",
    }


def margin_annual_interest(balance_borrowed: float, account_equity_proxy: float) -> dict[str, Any]:
    b = max(0.0, float(balance_borrowed))
    rate = MARGIN_PREMIUM_TIER_RATE if account_equity_proxy >= MARGIN_PREMIUM_TIER_BALANCE_USD else MARGIN_BASE_RATE_ANNUAL
    return {
        "borrowed": b,
        "rate_applied": rate,
        "est_annual_interest": round(b * rate, 2),
        "story": f"Tier story: **≥${MARGIN_PREMIUM_TIER_BALANCE_USD/1e6:.1f}M** equity → illustrative **{MARGIN_PREMIUM_TIER_RATE * 100:.2f}%**; else base **{MARGIN_BASE_RATE_ANNUAL * 100:.2f}%**.",
    }


def bond_cd_ladder(
    total_principal: float,
    rungs: int,
    years_span: float,
    annual_yield_assumption: float,
) -> pd.DataFrame:
    """Equal principal per rung; simple yield for teaching — not market pricing."""
    n = max(1, int(rungs))
    per = max(0.0, float(total_principal)) / n
    y = max(0.0, float(annual_yield_assumption))
    rows = []
    for i in range(n):
        mat_years = (i + 1) * (float(years_span) / n)
        income = per * y
        rows.append(
            {
                "Rung": i + 1,
                "Principal ($)": round(per, 2),
                "Maturity (yrs, story)": round(mat_years, 2),
                "Projected annual income ($, mock)": round(income, 2),
                "Type": "CD/Treasury mix (sim)",
            }
        )
    return pd.DataFrame(rows)


def mock_options_chain_extended(rows: int = 6) -> pd.DataFrame:
    rng = np.random.default_rng(11)
    strikes = np.linspace(420, 460, rows)
    out = []
    for k in strikes:
        out.append(
            {
                "strike": round(k, 2),
                "call_bid": round(rng.uniform(1, 12), 2),
                "call_ask": round(rng.uniform(1.2, 12.5), 2),
                "put_bid": round(rng.uniform(1, 10), 2),
                "put_ask": round(rng.uniform(1.2, 10.5), 2),
                "delta_c": round(rng.uniform(0.15, 0.75), 3),
                "gamma": round(rng.uniform(0.01, 0.06), 4),
                "theta": round(rng.uniform(-0.2, -0.02), 3),
                "vega": round(rng.uniform(0.05, 0.45), 3),
                "iv": round(rng.uniform(0.12, 0.35), 3),
            }
        )
    return pd.DataFrame(out)


def mock_bond_screener(n: int = 8) -> pd.DataFrame:
    kinds = ["Treasury", "Corporate IG", "Municipal", "Agency", "CD", "Money market"]
    rng = np.random.default_rng(3)
    rows = []
    for i in range(n):
        rows.append(
            {
                "CUSIP (sim)": f"SIM{rng.integers(100000, 999999)}",
                "Type": rng.choice(kinds),
                "YTM (mock %)": round(rng.uniform(2.5, 6.5), 2),
                "Maturity": f"{2026 + i // 3}-{1 + (i % 12):02d}",
            }
        )
    return pd.DataFrame(rows)
