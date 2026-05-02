"""
Robinhood Gold–style benefits — illustrative math only, not tax or legal advice.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Spec anchors (demo constants — real limits change yearly).
SUBSCRIPTION_USD_PER_MONTH = 5.0
TRIAL_DAYS = 30

# 2026: 3% match on contributions, IRS-style cap on *match* cited in spec ~$225.
IRA_MATCH_RATE = 0.03
IRA_MATCH_ANNUAL_CAP_USD = 225.0  # illustrative ceiling from assignment brief

ROLLOVER_MATCH_RATE = 0.01

APY_GOLD_CASH = 0.0335
APY_NON_GOLD_CASH = 0.0001

MARGIN_FREE_USD = 1000.0
MARGIN_RATE_ILLUSTRATIVE = 0.055  # ~5–6% band
MIN_ACCOUNT_FOR_MARGIN = 2000.0

STRATEGIES_FEE_BELOW_100K = 0.0025
STRATEGIES_FEE_CAP_USD = 250.0
STRATEGIES_THRESHOLD_USD = 100_000.0


@dataclass
class IraMatchResult:
    contribution: float
    raw_match: float
    capped_match: float
    note: str


def ira_contribution_match_gold(annual_contribution_usd: float) -> IraMatchResult:
    """3% match capped at illustrative annual match ceiling."""
    c = max(0.0, float(annual_contribution_usd))
    raw = c * IRA_MATCH_RATE
    capped = min(raw, IRA_MATCH_ANNUAL_CAP_USD)
    note = (
        f"Match is **{IRA_MATCH_RATE:.0%}** of contributions, deposited into the IRA (simulation). "
        f"Capped at **${IRA_MATCH_ANNUAL_CAP_USD:,.0f}/year** for this prototype (see IRS contribution limits for real eligibility)."
    )
    return IraMatchResult(
        contribution=c,
        raw_match=round(raw, 2),
        capped_match=round(capped, 2),
        note=note,
    )


def rollover_transfer_match(amount_usd: float) -> dict[str, Any]:
    """1% unlimited on rolled balances (illustrative)."""
    a = max(0.0, float(amount_usd))
    return {
        "rollover_amount": a,
        "match_rate": ROLLOVER_MATCH_RATE,
        "match_usd": round(a * ROLLOVER_MATCH_RATE, 2),
        "note": "No cap in this teaching model — production programs differ.",
    }


def uninvested_cash_yield(cash_balance_usd: float, gold_tier: bool) -> dict[str, Any]:
    bal = max(0.0, float(cash_balance_usd))
    apy = APY_GOLD_CASH if gold_tier else APY_NON_GOLD_CASH
    annual_interest = bal * apy
    return {
        "balance": bal,
        "apy": apy,
        "apy_pct_display": apy * 100,
        "estimated_annual_interest": round(annual_interest, 2),
        "note": "Rates are **variable**; FDIC sweep insurance described in real disclosures.",
    }


def margin_interest_illustrative(
    borrowed_usd: float,
    *,
    free_first_usd: float = MARGIN_FREE_USD,
    rate_on_rest: float = MARGIN_RATE_ILLUSTRATIVE,
) -> dict[str, Any]:
    b = max(0.0, float(borrowed_usd))
    chargeable = max(0.0, b - free_first_usd)
    annual_interest = chargeable * rate_on_rest
    return {
        "borrowed": b,
        "interest_free_slice": min(b, free_first_usd),
        "charged_balance": chargeable,
        "rate_on_charged_balance": rate_on_rest,
        "estimated_annual_interest": round(annual_interest, 2),
        "note": f"First **${free_first_usd:,.0f}** borrowed shown as interest-free for Gold (sim); remainder at illustrative **{rate_on_rest:.1%}**.",
    }


def margin_eligibility(account_value_usd: float) -> dict[str, Any]:
    v = float(account_value_usd)
    ok = v >= MIN_ACCOUNT_FOR_MARGIN
    return {
        "account_value": v,
        "meets_minimum_for_margin": ok,
        "minimum_required": MIN_ACCOUNT_FOR_MARGIN,
        "note": "Margin requires approval and risk disclosures in production.",
    }


def managed_portfolio_fee_gold(aum_usd: float) -> dict[str, Any]:
    """Robinhood Strategies–style fee story."""
    a = max(0.0, float(aum_usd))
    if a >= STRATEGIES_THRESHOLD_USD:
        fee = 0.0
        tier = "No management fee on assets over $100k (Gold story)"
    else:
        fee = min(STRATEGIES_FEE_CAP_USD, a * STRATEGIES_FEE_BELOW_100K)
        tier = "0.25% annual, capped at $250/year for Gold (story)"
    return {
        "aum": a,
        "estimated_annual_fee_usd": round(fee, 2),
        "tier_description": tier,
        "note": "Users can read **rationale per holding** in a full app; here we show fee logic only.",
    }
