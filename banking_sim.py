"""
Banking & payments — illustrative numbers only; not a bank, card issuer, or tax advisor.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Spec story constants (demo)
SAVINGS_APY_GOLD_BANKING = 0.04
FDIC_PASS_THROUGH_MAX_USD = 2_250_000.0
BANKING_LAUNCH_YEAR = 2025

GOLD_CARD_CASHBACK_RATE = 0.03
GOLD_CARD_ANNUAL_FEE_USD = 0.0

CASH_DELIVERY_MARKETS = ("SF Bay Area", "Dallas", "Miami", "NYC")  # illustrative

RVI_NAME = "Robinhood Ventures Fund I (illustrative)"
RVI_LISTING = "Example exchange-listed closed-end fund (sim)"
RVI_LAUNCH = "September 2025 (story)"
RVI_NO_MIN = "No $5M minimum — retail access via listed shares (teaching line)"

IRA_TYPES = ("Traditional IRA", "Roth IRA", "Rollover IRA")
IRA_2026_LIMIT_MOCK = 7_000.0  # illustrative single filer; real limits vary


@dataclass
class SavingsSnapshot:
    balance: float
    apy: float
    est_annual_interest: str


def gold_banking_savings_yield(savings_balance_usd: float) -> SavingsSnapshot:
    b = max(0.0, float(savings_balance_usd))
    apy = SAVINGS_APY_GOLD_BANKING
    est = b * apy
    return SavingsSnapshot(
        balance=b,
        apy=apy,
        est_annual_interest=f"~${est:,.2f}/yr at {apy * 100:.0f}% APY (simulated)",
    )


def gold_card_cashback_yearly(annual_spend: float) -> dict[str, Any]:
    s = max(0.0, float(annual_spend))
    cb = s * GOLD_CARD_CASHBACK_RATE
    return {
        "annual_spend": s,
        "cash_back_rate": GOLD_CARD_CASHBACK_RATE,
        "cash_back_usd": round(cb, 2),
        "annual_fee": GOLD_CARD_ANNUAL_FEE_USD,
        "issuer_story": "Issued via Coastal Community Bank / Visa (spec) — approval required in production.",
        "reinvest_story": "Cash back can sweep to **brokerage** or stay **cash** (sim toggle in UI).",
    }


def ira_room_remaining(ytd_contribution: float, limit: float | None = None) -> dict[str, Any]:
    lim = limit if limit is not None else IRA_2026_LIMIT_MOCK
    ytd = max(0.0, float(ytd_contribution))
    left = max(0.0, lim - ytd)
    return {"limit": lim, "ytd": ytd, "remaining": round(left, 2)}


def estate_tax_services_blurb() -> str:
    return (
        "**Estate planning & tax advisory** (Gold Banking story): tools and specialist access described "
        "in-app in production; here we show **scope only** — not personalized advice."
    )


def family_accounts_blurb() -> str:
    return (
        "**Family accounts:** household-level management and internal transfers within the ecosystem "
        "(simulated checklist — no real invites)."
    )


def private_markets_rvi_factsheet() -> dict[str, str]:
    return {
        "vehicle": RVI_NAME,
        "structure": "Publicly traded closed-end fund — exposure to pre-IPO-style sleeves (story)",
        "listing": RVI_LISTING,
        "minimum": RVI_NO_MIN,
        "launch": RVI_LAUNCH,
        "risk": "Listed price volatility; not the same as direct venture stakes.",
    }
