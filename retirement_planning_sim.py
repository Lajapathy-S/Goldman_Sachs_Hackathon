"""
§2.6 Retirement planning & account types — illustrative calculators and copy only.
"""

from __future__ import annotations

from typing import Any

# Story constants (not live IRS / plan data)
PLANS_ADMINISTERED_STORY = 28_800
TRAD_IRA_CATCH_UP_AGE = 50
RMD_START_AGE_STORY = 73  # illustrative policy timeline


# IRS Uniform Lifetime Table — selected divisors (illustrative subset)
RMD_DIVISOR: dict[int, float] = {
    73: 26.5,
    74: 25.5,
    75: 24.6,
    76: 23.7,
    77: 22.9,
    78: 22.0,
    79: 21.1,
    80: 20.2,
    81: 19.4,
    82: 18.5,
    83: 17.7,
    84: 16.8,
    85: 16.0,
}


def rmd_amount(balance: float, age: int) -> dict[str, Any]:
    """Minimum distribution story — divisor lookup with clamp."""
    if age < RMD_START_AGE_STORY:
        return {
            "rmd_required": False,
            "message": f"RMD rules generally begin at age **{RMD_START_AGE_STORY}+** in this illustration — confirm current IRS rules.",
            "annual_rmd": 0.0,
        }
    divisor = RMD_DIVISOR.get(age) or max(10.0, 120 - age)
    amt = max(0.0, float(balance)) / divisor
    return {
        "rmd_required": True,
        "age": age,
        "divisor": round(divisor, 2),
        "annual_rmd": round(amt, 2),
        "note": "Simplified Uniform Lifetime divisor — real RMDs use end-of-prior-year balance and IRS tables.",
    }


def traditional_ira_snapshot(
    contributed_ytd: float,
    annual_limit_story: float,
    age: int,
    magi: float,
    covered_by_workplace_plan: bool,
) -> dict[str, Any]:
    """Deductibility flags are rules-of-thumb for demo only."""
    deduct = True
    reason = "Workplace plan coverage off — deductibility often available within limits (verify)."
    if covered_by_workplace_plan:
        if magi > 136_000:
            deduct = False
            reason = "High MAGI + workplace plan — Traditional IRA deduction may be limited or zero (story threshold)."
        elif magi > 126_000:
            deduct = True
            reason = "Phase-out zone — partial deduction possible (sim)."
        else:
            reason = "Under phase-out — deduction may be allowed (sim)."
    catch_up = age >= TRAD_IRA_CATCH_UP_AGE
    limit = annual_limit_story + (1_000 if catch_up else 0)
    return {
        "contributed_ytd": contributed_ytd,
        "limit_story": limit,
        "remaining_room": max(0.0, round(limit - contributed_ytd, 2)),
        "tax_deductible_likely": deduct,
        "deductibility_note": reason,
        "catch_up_eligible": catch_up,
        "zero_funds_eligible": True,
        "rollover_support": "Inbound rollovers from qualified plans supported — direct trustee-to-trustee preferred.",
    }


def roth_contribution_eligibility(
    magi: float,
    filing: str,
    age: int,
) -> dict[str, Any]:
    """Phase-out story — not tax advice."""
    filing_l = (filing or "single").lower()
    limit_base = 7_000
    if age >= TRAD_IRA_CATCH_UP_AGE:
        limit_base += 1_000
    if "joint" in filing_l or filing_l == "mfj":
        full_below = 230_000
        zero_above = 240_000
    else:
        full_below = 146_000
        zero_above = 156_000
    if magi <= full_below:
        phase = "full"
        allowed = limit_base
        msg = "Within illustrated MAGI band for **full** Roth contribution (story)."
    elif magi >= zero_above:
        phase = "none"
        allowed = 0
        msg = "Above illustrated phase-out — **direct** Roth contribution may be $0; consider backdoor workflow if eligible."
    else:
        phase = "partial"
        frac = 1 - (magi - full_below) / (zero_above - full_below)
        allowed = round(limit_base * frac, 0)
        msg = "Inside phase-out — partial Roth contribution (sim linear phase-out)."
    return {
        "magi": magi,
        "filing": filing,
        "phase": phase,
        "max_contribution_story": int(allowed),
        "ira_limit_base_story": limit_base,
        "message": msg,
        "deadline_note": "Prior-year contributions often accepted until tax-day — confirm each year.",
    }


def roth_tax_free_growth(
    balance: float,
    annual_contribution: float,
    years: float,
    assumed_return: float,
) -> dict[str, Any]:
    """Future value of Roth vs taxable drag (simplified)."""
    r = assumed_return / 100.0
    n = max(0.1, float(years))
    b = float(balance)
    pmt = float(annual_contribution)
    fv = b * (1 + r) ** n
    if r != 0:
        fv += pmt * ((1 + r) ** n - 1) / r
    else:
        fv += pmt * n
    tax_drag = 0.18
    r_tax = r * (1 - tax_drag)
    fv_tax = b * (1 + r_tax) ** n
    if r_tax != 0:
        fv_tax += pmt * ((1 + r_tax) ** n - 1) / r_tax
    else:
        fv_tax += pmt * n
    return {
        "years": n,
        "assumed_return_pct": assumed_return,
        "roth_future_value_est": round(fv, 0),
        "taxable_future_value_est_story": round(fv_tax, 0),
        "note": "Roth qualified withdrawals illustrated as tax-free; taxable side uses a rough drag rate — not advice.",
    }


def backdoor_roth_steps() -> list[str]:
    return [
        "Contribute to Traditional IRA (often non-deductible if income above deductibility limits).",
        "Wait for settlement — avoid commingling with deductible basis when possible (tracking Form 8606).",
        "Convert Traditional balance to Roth — report conversion on taxes; pro-rata rule may apply to pre-tax balances.",
        "Invest inside Roth for long-term tax-free growth.",
    ]


def rollover_ira_info() -> dict[str, Any]:
    return {
        "support_team": "Dedicated rollover specialists — **phone** queue with callback (story).",
        "sources": ["401(k)", "403(b)", "457", "other qualified plans"],
        "direct_rollover": "Funds sent trustee-to-trustee — generally **no** 60-day clock; preferred.",
        "sixty_day": "You receive a check payable to you — must deposit within **60 days** to IRA; one rollover per year limits may apply.",
        "checklist": [
            "Locate latest plan statement and beneficiary info.",
            "Choose Traditional vs Roth destination based on source tax treatment.",
            "Confirm withholding — direct rollover usually avoids 20% withholding trap.",
        ],
    }


def sep_simple_snapshot(
    net_self_employment: float,
    employees: int,
    account_type: str,
) -> dict[str, Any]:
    """SEP vs SIMPLE contribution story."""
    t = (account_type or "SEP").upper()
    if "SIMPLE" in t:
        deferral_limit = 16_000
        match_story = "Employer match up to 3% (or fixed 2%) — illustration only."
        return {
            "plan": "SIMPLE IRA",
            "employee_deferral_limit_story": deferral_limit,
            "employer_match_story": match_story,
            "employees": employees,
            "note": "SIMPLE has startup and maintenance rules — confirm IRS eligibility.",
        }
    sep_cap_pct = 0.25
    sep_max = 69_000
    contrib = min(sep_max, net_self_employment * sep_cap_pct)
    return {
        "plan": "SEP-IRA",
        "compensation_basis_story": round(net_self_employment, 0),
        "employer_contribution_est": round(contrib, 0),
        "max_percent_story": f"Up to **{sep_cap_pct:.0%}** of compensation, subject to annual cap (story numbers).",
        "employees": employees,
        "note": "SEP funded by employer only; deadlines differ from employee deferrals.",
    }


def employer_401k_view(
    balance: float,
    deferral_pct: float,
    employer_match_pct: float,
    match_cap_pct: float,
) -> dict[str, Any]:
    salary_story = 120_000.0
    you = salary_story * (deferral_pct / 100.0)
    match_raw = salary_story * (employer_match_pct / 100.0)
    match_capped = min(match_raw, salary_story * (match_cap_pct / 100.0))
    return {
        "plan_participants_story": PLANS_ADMINISTERED_STORY,
        "your_balance_sim": round(balance, 0),
        "fund_lineup_count_story": 28,
        "your_contribution_pct": deferral_pct,
        "your_contribution_dollars_story": round(you, 0),
        "employer_match_rate_pct": employer_match_pct,
        "employer_match_dollars_story": round(match_capped, 0),
        "vesting_note": "Employer match may vest on a schedule — check SPD.",
    }


def state_529_catalog() -> list[dict[str, Any]]:
    return [
        {"State": "CA", "Plan nickname": "ScholarShare", "deduction_story": "No state income tax deduction for CA residents."},
        {"State": "NY", "Plan nickname": "NY Saves", "deduction_story": "Up to illustrated $5k single / $10k MFJ state deduction (story)."},
        {"State": "NJ", "Plan nickname": "NJBEST", "deduction_story": "State credit/deduction rules vary — verify annually."},
        {"State": "PA", "Plan nickname": "PA 529", "deduction_story": "Broad contribution deduction story — any state's plan may qualify for PA filers (illustrative)."},
        {"State": "VT", "Plan nickname": "VT Higher Ed", "deduction_story": "Marginal rate × contribution subject to cap (story)."},
    ]


def college_529_goal_tracker(
    current_balance: float,
    monthly_contribution: float,
    years_to_enrollment: float,
    annual_return_pct: float,
    college_cost_year_one: float,
) -> dict[str, Any]:
    rm = (annual_return_pct / 100.0) / 12.0
    months = max(1, int(round(max(0.1, years_to_enrollment) * 12)))
    pv = float(current_balance)
    pmt = float(monthly_contribution)
    if rm == 0:
        fv = pv + pmt * months
    else:
        fv = pv * (1 + rm) ** months + pmt * ((1 + rm) ** months - 1) / rm
    need = college_cost_year_one * 4 * 0.65
    gap = need - fv
    return {
        "projected_balance_at_enrollment": round(fv, 0),
        "illustrative_four_year_need_story": round(need, 0),
        "funding_gap_story": round(gap, 0),
        "message": "Goal tracker compares projected savings to a rough multi-year cost slice — tune assumptions.",
    }


def state_tax_benefit_estimate(state: str, contribution: float, marginal_rate_story: float) -> dict[str, Any]:
    """Rough deduction × rate where applicable."""
    st_u = (state or "").upper()
    catalog = {row["State"]: row for row in state_529_catalog()}
    row = catalog.get(st_u, list(catalog.values())[0])
    cap = 10_000 if st_u in ("NY", "NJ") else 15_000
    deductible = min(contribution, cap)
    benefit = deductible * (marginal_rate_story / 100.0)
    return {
        "state": st_u,
        "contribution": contribution,
        "deduction_story": row["deduction_story"],
        "estimated_state_benefit": round(benefit, 0),
        "note": "Not tax advice — states change rules frequently.",
    }
