"""
Schwab Bank & cash management — story-level copy for coursework (not live rates or rules).
"""

from __future__ import annotations

from typing import Any

FDIC_LIMIT_PER_CATEGORY_STORY = 250_000


def high_yield_investor_checking_story() -> dict[str, Any]:
    return {
        "product": "Schwab Bank High Yield Investor Checking",
        "minimum_balance": "No minimum balance requirement (story)",
        "monthly_fee": "No monthly maintenance fee (story)",
        "foreign_txn": "No **foreign transaction** fees on eligible purchases (story)",
        "atm": "**Unlimited** worldwide **ATM fee rebates** — surcharges from other banks rebated (story)",
        "fdic": f"**FDIC insured** up to standard limits (e.g. **${FDIC_LIMIT_PER_CATEGORY_STORY:,}** per ownership category — confirm coverage)",
        "debit": "Visa® debit with **Visa Zero Liability** for unauthorized card use (terms apply)",
    }


def investor_savings_story(illustrative_apy_pct: float = 3.45) -> dict[str, Any]:
    return {
        "product": "Schwab Bank Investor Savings",
        "linkage": "High-yield **savings** linked to **Schwab brokerage** — single sign-on (story)",
        "apy": f"**Competitive** variable APY — illustration **{illustrative_apy_pct:.2f}%** (not a live rate)",
        "fdic": f"FDIC insured up to **${FDIC_LIMIT_PER_CATEGORY_STORY:,}** per depositor, per bank, per ownership (story)",
        "transfers": "Transfers between **savings** and **brokerage** are **immediate** for available cash (story)",
    }


def one_interest_brokerage_sweep_story(sweep_apy_illustrative: float = 2.10) -> dict[str, Any]:
    return {
        "feature": "Schwab One® Interest Feature (Brokerage cash)",
        "mechanic": "Uninvested **brokerage cash** may earn interest via **Schwab Bank sweep deposit** programs (story)",
        "rate": f"**Variable** rate — illustrative **{sweep_apy_illustrative:.2f}%** on swept balances (not live)",
        "visibility": "Sweep balance & accrued interest shown on **portfolio dashboard** alongside positions",
    }


def mobile_check_deposit_story() -> dict[str, Any]:
    return {
        "feature": "Mobile Check Deposit",
        "channel": "**Schwab Mobile** app — photograph check **front & back**",
        "availability": "Funds typically available within **1 business day** for most checks — holds possible (story)",
        "limits": "Daily / rolling deposit limits apply — disclosed in app",
    }


def bill_pay_and_transfers_story() -> dict[str, Any]:
    return {
        "suite": "Bill Pay & Transfers",
        "bill_pay": "Schedule **bill payments** from Schwab checking to payees (story)",
        "internal": "Move money between **Schwab** accounts (checking, savings, brokerage cash)",
        "external": "ACH **to / from** linked external bank accounts — verification required",
        "recurring": "**Recurring** transfers supported (story)",
        "wires": "**Domestic** and **international** wire transfers available — fees & FX spreads disclosed at send",
    }


def fdic_sweep_intelligent_portfolios_story() -> dict[str, Any]:
    return {
        "program": "FDIC Sweep Protection (Intelligent Portfolios cash)",
        "mechanic": (
            "Uninvested **cash** in **Schwab Intelligent Portfolios** is **swept** to **FDIC-insured** bank deposit accounts "
            f"up to applicable limits (e.g. **${FDIC_LIMIT_PER_CATEGORY_STORY:,}** coverage illustration — confirm ownership buckets)."
        ),
        "disclosure": (
            "Schwab & affiliates may **earn income** on **sweep deposits** — relationship disclosed in program materials (story)."
        ),
        "purpose": "Keeps idle cash insured within bank limits vs leaving raw brokerage cash uninsured",
    }
