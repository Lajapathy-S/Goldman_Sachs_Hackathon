"""
Robo-advisory & managed accounts — Fidelity-style tier stories (mock only).
"""

from __future__ import annotations

from typing import Any

import pandas as pd

# Thresholds (story — not live eligibility rules)
GO_MINIMUM_FIRST_INVESTMENT = 10.0
GO_ZERO_FEE_CAP_USD = 25_000.0
GO_ENHANCED_MIN_USD = 25_000.0
WEALTH_SERVICES_MIN_USD = 50_000.0
SMA_MIN_USD = 200_000.0
WEALTH_MANAGEMENT_MIN_USD = 500_000.0

KIPLINGER_AWARD_STORY = "Best Robo-Advisor — **Kiplinger 2025** (story)"
FLEX_FUNDS_NOTE = "Invests via **Fidelity Flex** mutual funds in production narrative."


def go_fee_story(aum_usd: float) -> dict[str, Any]:
    a = max(0.0, float(aum_usd))
    if a <= GO_ZERO_FEE_CAP_USD:
        fee_label = "$0 program fee (balances under $25k story)"
        tier = "Fidelity Go — standard"
    else:
        fee_label = "Enhanced tier — advisory/coaching wrap (story; check live schedule)"
        tier = "Fidelity Go — personalized planning"
    return {"aum": a, "tier_label": tier, "fee_summary": fee_label}


def managed_account_tier(total_investable_usd: float) -> dict[str, Any]:
    """Maps balance bands to service narratives."""
    x = float(total_investable_usd)
    services = []
    if x >= GO_MINIMUM_FIRST_INVESTMENT:
        services.append("✓ **Fidelity Go** eligible ($10+ to start)")
    if x >= GO_ENHANCED_MIN_USD:
        services.append("✓ **Go — Personalized Planning & Advice** (coaching story)")
    if x >= WEALTH_SERVICES_MIN_USD:
        services.append("✓ **Fidelity Wealth Services** — human discretionary (~fee % of AUM)")
    if x >= SMA_MIN_USD:
        services.append("✓ **Strategic Disciplines (SMA)** — direct securities sleeves")
    if x >= WEALTH_MANAGEMENT_MIN_USD:
        services.append("✓ **Fidelity Wealth Management** — full HNW team")
    return {"balance": x, "service_lines": services, "next_review": "Annual account review (Go story)"}


def sma_strategies_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Strategy": "Large-cap equity SMA", "Min (story)": f"${SMA_MIN_USD:,.0f}", "Focus": "Blue-chip US"},
            {"Strategy": "Bond ladder SMA", "Min (story)": f"${SMA_MIN_USD:,.0f}", "Focus": "Income / maturity stagger"},
            {"Strategy": "Tax-managed equity SMA", "Min (story)": f"${SMA_MIN_USD:,.0f}", "Focus": "After-tax growth"},
        ]
    )


def model_portfolio_catalog() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Risk profile": "Conservative",
                "ETF sleeve (sim %)": "25 equity / 75 fixed",
                "Mutual fund sleeve (sim %)": "30 equity / 70 fixed",
            },
            {
                "Risk profile": "Moderate",
                "ETF sleeve (sim %)": "50 / 50",
                "Mutual fund sleeve (sim %)": "48 / 52",
            },
            {
                "Risk profile": "Growth",
                "ETF sleeve (sim %)": "70 / 30",
                "Mutual fund sleeve (sim %)": "72 / 28",
            },
            {
                "Risk profile": "Aggressive growth",
                "ETF sleeve (sim %)": "90 / 10",
                "Mutual fund sleeve (sim %)": "88 / 12",
            },
        ]
    )


def wealth_fee_illustrative(aum: float, tier: str) -> str:
    """Placeholder fee language — not an offer."""
    if tier == "fws":
        return f"Typical **discretionary** fee quoted as **~0.50%–1.00%** AUM annually (illustrative band)."
    if tier == "fwm":
        return "**Negotiated** advisory fee for comprehensive planning — disclosed in advisory agreement (sim)."
    return "See firm CRS & brochure."
