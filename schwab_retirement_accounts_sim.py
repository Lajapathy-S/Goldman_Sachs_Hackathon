"""
Schwab IRA, workplace, custodial, charitable & 529 — story-level copy (coursework).
"""

from __future__ import annotations

from typing import Any

NERDWALLET_IRA_RANK_STORY = "#1 broker for IRA investors — **NerdWallet 2026** (story)"


def schwab_traditional_roth_ira_story() -> dict[str, Any]:
    return {
        "accounts": "Traditional IRA & Roth IRA — both available at Schwab (story)",
        "recognition": NERDWALLET_IRA_RANK_STORY,
        "features": [
            "**Contribution tracking** & tax-year deadline reminders",
            "**RMD** tools for Traditional IRA (rules per IRS)",
            "**Backdoor Roth** workflow support where eligible — Form 8606 tracking reminders",
        ],
        "minimum": "**No** account minimum for opening IRAs (story)",
        "note": "Limits & eligibility change annually — confirm IRS / plan notices.",
    }


def schwab_rollover_ira_story() -> dict[str, Any]:
    return {
        "product": "Rollover IRA",
        "support": "**Dedicated rollover support center** — specialists for employer-plan moves (story)",
        "sources": ["401(k)", "403(b)", "457", "other qualified plans"],
        "direct_rollover": "**Trustee-to-trustee** transfer preferred — avoids mandatory **20% withholding** on eligible distributions (story)",
        "checklist": ["Gather statement", "Choose Traditional vs Roth destination", "Confirm loan payoff if any"],
    }


def schwab_small_business_retirement_story() -> dict[str, Any]:
    return {
        "suite": "Small Business Retirement — SEP, SIMPLE, Individual 401(k)",
        "solo_401k": "**Individual (solo) 401(k)** with **Designated Roth** deferrals where plan permits (story)",
        "limits": "Higher **employer** profit-sharing / SEP % of comp vs IRAs — calculators in workplace hub (story)",
        "deliverables": ["Contribution calculators", "Plan documents store", "Payroll integration guides"],
        "audience": "Self-employed & small teams — eligibility rules vary by entity type.",
    }


def schwab_employer_401k_services_story() -> dict[str, Any]:
    return {
        "program": "401(k) Plans — Schwab Retirement Plan Services",
        "employers": "Recordkeeping, investment menu, fiduciary education — employer-sponsored (story)",
        "employee_experience": "**Employee portal** ties to **personal Schwab.com** login — **unified** balances & contributions",
        "features": ["Deferral changes", "Match tracking", "Loan / distribution requests per plan rules"],
    }


def schwab_custodial_accounts_story() -> dict[str, Any]:
    return {
        "registration": "Custodial accounts — **UGMA / UTMA**",
        "control": "**Custodian** (parent/guardian) directs investments until termination",
        "termination": "Assets transfer to minor at **state-specific age of majority** — flagged in advance (story)",
        "education": "Minor gains reporting — kiddie tax considerations — consult tax advisor.",
    }


def schwab_charitable_daf_story() -> dict[str, Any]:
    return {
        "program": "Schwab Charitable — Donor-Advised Fund (DAF)",
        "contributions": "Fund with **cash** or **appreciated securities** — potential **immediate** charitable deduction (story)",
        "granting": "**Recommend grants** to IRS-qualified charities **over time** — invested pool may grow tax-free for charity",
        "advantages": "Avoid capital gains on donated appreciated stock — still subject to AGI limits & appraisal rules",
        "governance": "Schwab Charitable™ is a public charity — separate from brokerage affiliate disclosures.",
    }


def schwab_529_alliance_story() -> dict[str, Any]:
    return {
        "program": "529 College Savings Plans",
        "alliance": "Offered in alliance with **state plan administrators** — multi-state menu on Schwab.com (story)",
        "tools": [
            "Goal tracker vs projected college costs",
            "Savings gap analysis",
            "Beneficiary changes & qualified expense tracking",
        ],
        "tax_note": "Some states offer deductions/credits — federal tax-free growth for qualified education expenses.",
    }
