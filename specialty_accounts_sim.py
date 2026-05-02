"""
HSA, Youth, Trust, Custodial (UGMA/UTMA) — simulation only.
"""

from __future__ import annotations

import hashlib
from typing import Any

# Illustrative annual contribution caps (verify IRS each year)
HSA_LIMIT_INDIVIDUAL_STORY = 4_300
HSA_LIMIT_FAMILY_STORY = 8_750
HSA_CATCH_UP_55_STORY = 1_000

QUALIFIED_EXPENSE_LABELS = (
    "Medical / dental / vision copays & deductibles",
    "Prescriptions & OTC with Rx where required",
    "Qualified long-term care premiums (limits apply)",
    "COBRA premiums while eligible",
    "Certain Medicare premiums when eligible",
)

TEEN_EDUCATION_MODULES = (
    "What is a stock vs ETF?",
    "Why diversification beats picking one ticker",
    "How parental limits & approvals work",
    "Paper gains vs taxes — basics",
    "Scams & social media stock hype",
)


def hsa_contribution_room(
    coverage: str,
    age: int,
    contributed_ytd: float,
) -> dict[str, Any]:
    base = HSA_LIMIT_FAMILY_STORY if coverage.lower() == "family" else HSA_LIMIT_INDIVIDUAL_STORY
    if age >= 55:
        base += HSA_CATCH_UP_55_STORY
    rem = max(0.0, round(base - contributed_ytd, 2))
    return {
        "coverage_tier": coverage,
        "annual_limit_story": base,
        "contributed_ytd": contributed_ytd,
        "remaining_room": rem,
        "catch_up_applies": age >= 55,
        "investment_eligible": True,
        "lineup_note": "Invest in eligible HSA brokerage window — Fidelity funds & ETFs when offered (story).",
    }


def hsa_tax_benefit_estimate(
    payroll_contribution: float,
    employer_contribution: float,
    marginal_federal_pct: float,
    state_tax_pct: float,
) -> dict[str, Any]:
    """Rough avoided tax on contributions — not tax advice."""
    total_in = payroll_contribution + employer_contribution
    fed_save = payroll_contribution * (marginal_federal_pct / 100.0)
    st_save = payroll_contribution * (state_tax_pct / 100.0) if state_tax_pct else 0
    fica_story = payroll_contribution * 0.0765  # illustrative if via cafeteria only
    return {
        "payroll_contribution": payroll_contribution,
        "employer_seed": employer_contribution,
        "est_federal_avoided": round(fed_save, 0),
        "est_state_avoided": round(st_save, 0),
        "fica_story_if_applicable": round(fica_story, 0),
        "triple_tax_story": "Contributions often avoid fed + state + FICA when run through qualifying payroll; growth & qualified withdrawals tax-free for medical.",
        "note": "Illustrative — actual taxes depend on payroll setup and domicile.",
    }


def mock_qualified_expenses_ledger() -> list[dict[str, Any]]:
    rows = [
        {"Date": "2026-01-04", "Payee": "City Dental", "Amount": 120.0, "Category": "Dental"},
        {"Date": "2026-01-18", "Payee": "Regional Pharmacy", "Amount": 44.5, "Category": "Prescription"},
        {"Date": "2026-02-02", "Payee": "Vision Care Co.", "Amount": 95.0, "Category": "Vision"},
        {"Date": "2026-02-20", "Payee": "Specialty Clinic", "Amount": 350.0, "Category": "Medical"},
        {"Date": "2026-03-01", "Payee": "OTC Retail", "Amount": 28.0, "Category": "OTC (qualified)"},
    ]
    return rows


def youth_account_profile(age: int) -> dict[str, Any]:
    ok = 13 <= age <= 17
    return {
        "eligible": ok,
        "age": age,
        "parental_oversight": "Guardian approves trades above limits; statements shared (story).",
        "minimum": 0,
        "products": ["Stocks", "ETFs"],
        "education_modules": list(TEEN_EDUCATION_MODULES),
        "message": "Youth Account available for ages **13–17** with guardian relationship (sim).",
    }


def trust_account_overview(trust_type: str) -> dict[str, Any]:
    t = (trust_type or "revocable").lower()
    irrev = "irrev" in t
    return {
        "trust_type_story": "Irrevocable trust" if irrev else "Revocable living trust",
        "trustee_tools": [
            "Cash & investment allocation across linked accounts",
            "Distribution requests with memo / beneficiary purpose tracking",
            "Document vault for trust instrument & amendments",
            "Annual review checklist — crummey notices, GRAT schedules where applicable (story)",
        ],
        "estate_center": [
            "Beneficiary audit across IRAs, 401(k)s, pay-on-death accounts",
            "Titling review — trust as owner vs individual",
            "Letter of intent & digital asset inventory",
        ],
        "beneficiary_review_prompts": [
            "Has anyone married/divorced since last review?",
            "Do percentages still sum to 100% across primary/contingent?",
            "Are special needs trusts correctly referenced where needed?",
        ],
    }


def custodial_account_snapshot(
    account_flavor: str,
    minor_age: int,
    state: str,
    balance: float,
) -> dict[str, Any]:
    """UGMA vs UTMA + age of majority story."""
    flavor = (account_flavor or "UTMA").upper()
    st_key = (state or "CA").upper()
    # Illustrative majority ages — many states 18–21 for UTMA
    majority = _majority_age_story(st_key, flavor)
    if minor_age >= majority:
        months_to = 0
    else:
        months_to = int(max(0, majority - minor_age) * 12)
    # Flag when at/over majority or entering final year before termination (story)
    transfer_at_majority_flag = minor_age >= majority or minor_age == majority - 1
    return {
        "registration": flavor,
        "minor_age": minor_age,
        "state": st_key,
        "age_of_majority_story": majority,
        "months_until_majority_est": months_to,
        "transfer_at_majority_flag": transfer_at_majority_flag,
        "balance_story": round(balance, 2),
        "custodian_note": "Custodian manages until termination — UTMA/UGMA rules vary by state (sim).",
    }


def _majority_age_story(state: str, flavor: str) -> int:
    h = int(hashlib.md5(f"{state}|{flavor}".encode()).hexdigest()[:6], 16)
    # UTMA often 18–21 depending on state — pin a deterministic age 18-21
    return 18 + (h % 4)

