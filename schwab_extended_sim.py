"""
Schwab-style extended products — OneSource, extended hours, crypto, margin, global, IPO (simulation).
"""

from __future__ import annotations

import random
from typing import Any

MUTUAL_FUND_ONESOURCE_COUNT_STORY = 2_000
ASSET_MANAGERS_COUNT_STORY = 58
ONESOURCE_LAUNCH_NOTE = "Broad lineup expanded to ~2,000 funds across 58 asset managers as of 2025 (story)."

EXTENDED_HOURS_SYMBOLS_STORY = 1_100
EXTENDED_HOURS_SCHEDULE = "24 hours / day, 5 days / week on thinkorswim — launched **2025** (story)."

CRYPTO_ASSETS_STORY = ("Bitcoin", "Ethereum")
CRYPTO_OFFERED_THROUGH = "Schwab Premier Bank, SSB (story)"
CRYPTO_NOTICE = "Customers notified when Schwab Crypto™ account becomes available in their region."

MARGIN_BASE_RATE_STORY = 11.5  # illustrative
MAINTENANCE_REQUIREMENT_PCT = 0.30


def mutual_fund_onesource_summary() -> dict[str, Any]:
    return {
        "program": "Mutual Fund OneSource®",
        "no_transaction_fee_funds_story": MUTUAL_FUND_ONESOURCE_COUNT_STORY,
        "asset_managers_story": ASSET_MANAGERS_COUNT_STORY,
        "detail": ONESOURCE_LAUNCH_NOTE,
        "trade_fee_story": "$0 transaction fee on participating funds — confirm fund-specific expenses.",
    }


def mock_onesource_fund_sample(n: int = 8, seed: int = 31) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    families = ["American Funds", "Vanguard", "T. Rowe Price", "iShares mutual fund", "DFA", "PIMCO"]
    cats = ["Large cap", "Bond core", "International", "Target date", "Municipal", "Sector equity"]
    rows = []
    for i in range(n):
        er = round(rng.uniform(0.0, 0.85), 2)
        rows.append(
            {
                "Fund name (sim)": f"Sample OneSource Fund {i+1}",
                "Manager family": rng.choice(families),
                "Category": rng.choice(cats),
                "Expense ratio %": er,
                "NTF on OneSource": "Yes",
            }
        )
    return rows


def extended_hours_trading_story() -> dict[str, Any]:
    return {
        "platforms": "thinkorswim — desktop, web, mobile",
        "symbols_story": f"{EXTENDED_HOURS_SYMBOLS_STORY:,}+ US-listed stocks & ETFs",
        "session": EXTENDED_HOURS_SCHEDULE,
        "liquidity_note": "Overnight sessions can have wider spreads — use limits (story).",
    }


def schwab_crypto_account_story() -> dict[str, Any]:
    return {
        "product": "Schwab Crypto™ account",
        "assets": list(CRYPTO_ASSETS_STORY),
        "offered_through": CRYPTO_OFFERED_THROUGH,
        "activity": "Direct buy/sell of Bitcoin and Ethereum when enabled (story)",
        "notification": CRYPTO_NOTICE,
        "risk": "Crypto is volatile and not SIPC-protected like securities — read disclosures.",
    }


def margin_account_snapshot(
    equity: float,
    debit_balance: float,
    base_rate_pct: float | None = None,
) -> dict[str, Any]:
    rate = float(base_rate_pct if base_rate_pct is not None else MARGIN_BASE_RATE_STORY)
    equity_f = max(0.0, float(equity))
    debit = max(0.0, float(debit_balance))
    # Illustrative: additional stock buying power from Reg T–style 2x notional vs cash (not advice).
    reg_t_notional = max(0.0, equity_f * 2.0)
    buying_power_story = round(max(0.0, reg_t_notional - debit), 0)
    return {
        "equity": round(equity_f, 2),
        "margin_debit": round(debit, 2),
        "disclosed_base_rate_story_pct": rate,
        "maintenance_requirement_pct_story": MAINTENANCE_REQUIREMENT_PCT,
        "margin_buying_power_story": buying_power_story,
        "dashboard_note": "Buying power surfaced prominently on balances / margin summary (story).",
        "alerts": "Margin call alerts via **push**, **email**, and **SMS** when thresholds breached (story).",
    }


def international_trading_story() -> dict[str, Any]:
    return {
        "global_account": "Trade international equities through **Global Account** workflow — FX & settlement rules apply (story).",
        "adrs": "Many foreign names accessible as **ADRs** in standard brokerage — trade in USD during US hours.",
        "research": "Country / currency risk disclosures shown before ticket submission (story).",
    }


def ipo_and_new_issues_story() -> dict[str, Any]:
    return {
        "programs": ["New issues", "IPO allocations", "Secondary offerings where offered"],
        "eligibility": "Household asset tiers & suitability screens — not all clients receive allocations (story).",
        "schwab_equity_ratings": "IPO candidates may display Schwab Equity Ratings® as one input — not a recommendation alone.",
    }


def mock_ipo_calendar_rows(n: int = 6, seed: int = 44) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    sectors = ["Tech", "Healthcare", "Consumer", "Industrial", "Financials"]
    rows = []
    for i in range(n):
        rat = rng.choice(["A", "B", "C", "D", "F"])
        rows.append(
            {
                "Issuer (sim)": f"Example Co {i+1} IPO",
                "Sector": rng.choice(sectors),
                "Expected range (sim)": f"${rng.randint(18, 42)}–${rng.randint(22, 48)}",
                "Schwab Equity Rating® (story)": rat,
                "Offering type": rng.choice(["IPO", "Follow-on", "Convertible"]),
            }
        )
    return rows
