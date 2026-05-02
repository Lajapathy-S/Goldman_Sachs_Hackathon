"""
Schwab Intelligent Portfolios (SIP) — Base & options — simulation only.
"""

from __future__ import annotations

from datetime import date
from typing import Any

SIP_MINIMUM_OPEN_USD = 5_000
SIP_ETF_COUNT_STORY = 53
SIP_ASSET_CLASS_BUCKETS_STORY = 20
REBALANCE_DRIFT_THRESHOLD = 0.05  # 5%
TLH_MIN_TAXABLE_USD = 50_000


def sip_base_program_story() -> dict[str, Any]:
    return {
        "program": "Schwab Intelligent Portfolios (SIP) — Base",
        "management_fee_story": "$0 program management fee — ETF expense ratios still apply",
        "construction": f"**{SIP_ETF_COUNT_STORY}** ETFs spanning **{SIP_ASSET_CLASS_BUCKETS_STORY}** asset-class sleeves (story)",
        "minimum_open": f"${SIP_MINIMUM_OPEN_USD:,} to open",
        "onboarding": "Recommended portfolio from **risk questionnaire** — auto **rebalancing**, no separate advisory fee for base SIP (story).",
    }


def risk_questionnaire_axes() -> dict[str, Any]:
    return {
        "steps": [
            "Investment **horizon** (when will you spend this money?)",
            "**Income stability** / emergency cushion",
            "**Loss tolerance** — largest dip you'd tolerate without selling in fear",
            "**Goal type** — growth, income, capital preservation, major purchase",
        ],
        "output": "Maps answers to a risk score → **target allocation** with plain-language rationale (story).",
    }


def recommended_allocation(
    horizon_years: float,
    loss_tolerance: str,
    goal: str,
    income_stable: bool,
) -> dict[str, Any]:
    """
    Toy mapping → illustrative weights (aggregated sleeves for chart).
    """
    lt = (loss_tolerance or "moderate").lower()
    base_eq = 0.55
    if "low" in lt or "conservative" in lt:
        base_eq = 0.35
    elif "high" in lt or "aggressive" in lt:
        base_eq = 0.78
    if horizon_years >= 15:
        base_eq += 0.07
    elif horizon_years < 4:
        base_eq -= 0.12
    if "income" in (goal or "").lower():
        base_eq -= 0.08
    if not income_stable:
        base_eq -= 0.05
    base_eq = max(0.22, min(0.88, base_eq))
    fi = round(1.0 - base_eq, 4)
    # Split equity into regions & alts story
    us = round(base_eq * 0.58, 4)
    intl = round(base_eq * 0.22, 4)
    em = round(base_eq * 0.08, 4)
    reit = round(base_eq * 0.07, 4)
    comm = round(base_eq * 0.05, 4)
    gov = round(fi * 0.45, 4)
    corp = round(fi * 0.25, 4)
    tips = round(fi * 0.15, 4)
    cash = max(0.0, round(1.0 - (us + intl + em + reit + comm + gov + corp + tips), 4))
    weights = {
        "US equity": us,
        "International equity": intl,
        "Emerging markets": em,
        "Real estate (REITs)": reit,
        "Commodities": comm,
        "Gov / Treasury bonds": gov,
        "Corporate bonds": corp,
        "Inflation-protected (TIPS)": tips,
        "Cash": cash,
    }
    s = sum(weights.values())
    if s > 0:
        weights = {k: round(v / s, 4) for k, v in weights.items()}
    rationale = (
        f"Horizon ~**{horizon_years:.1f} yrs**, goal **{goal}**, loss posture **{loss_tolerance}** → "
        f"{'higher' if base_eq > 0.55 else 'moderate' if base_eq > 0.4 else 'lower'} equity tilt "
        f"({'stable income' if income_stable else 'buffer for income uncertainty'})."
    )
    return {"weights": weights, "rationale_plain_language": rationale, "risk_inputs_echo": {
        "horizon_years": horizon_years,
        "loss_tolerance": loss_tolerance,
        "goal": goal,
        "income_stable": income_stable,
    }}


def rebalance_story(current_weights: dict[str, float], target_weights: dict[str, float]) -> dict[str, Any]:
    drifts = []
    for k in target_weights:
        cur = current_weights.get(k, 0.0)
        tgt = target_weights[k]
        d = abs(cur - tgt)
        drifts.append({"sleeve": k, "drift": round(d, 4), "trigger": d >= REBALANCE_DRIFT_THRESHOLD})
    fired = any(x["trigger"] for x in drifts)
    return {
        "threshold": f"{REBALANCE_DRIFT_THRESHOLD:.0%}+ drift vs target",
        "drift_rows": drifts,
        "rebalance_required_story": fired,
        "execution": "House executes trades to restore targets — **internal** basket trades (story)",
        "user_notification": "Your portfolio was rebalanced on **[date]** — push/in-app + email (story).",
    }


def tlh_sip_story(taxable_balance: float) -> dict[str, Any]:
    ok = float(taxable_balance) >= TLH_MIN_TAXABLE_USD
    return {
        "feature": "Automated Tax-Loss Harvesting (SIP)",
        "eligible": ok,
        "minimum_taxable_aum_story": f"${TLH_MIN_TAXABLE_USD:,}+",
        "process": (
            "Daily scan for **unrealized losses** → sell loss lot → **immediately** swap into "
            "**highly correlated substitute ETF** to keep factor exposure (wash-sale rules apply — story)."
        ),
        "location": "Taxable accounts only — not IRAs (story).",
    }


def tlh_notification_bundle() -> dict[str, Any]:
    return {
        "channels": ["Push notification", "Email"],
        "content": "Each harvest event — lots sold, substitute ticker, est. **tax benefit** in dollars (illustrative)",
        "annual_report": "Year-end **tax savings summary** — not tax advice; share with CPA",
    }


def twenty_asset_class_reference() -> list[dict[str, str]]:
    return [
        {"Class": "US large-cap equity", "Plain English": "Big US companies across industries — core growth engine."},
        {"Class": "US small-cap equity", "Plain English": "Smaller US firms — higher volatility, diversification."},
        {"Class": "International developed equity", "Plain English": "Large companies abroad in mature economies."},
        {"Class": "Emerging markets equity", "Plain English": "Faster-growing economies — extra volatility."},
        {"Class": "Real estate (REITs)", "Plain English": "Property-related income streams — not direct housing."},
        {"Class": "Government bonds", "Plain English": "Treasury / agency — ballast when stocks dip."},
        {"Class": "Investment-grade corporate bonds", "Plain English": "Loans to stable companies — yield vs Treasuries."},
        {"Class": "High-yield bonds", "Plain English": "Lower credit quality — extra yield, extra risk."},
        {"Class": "Inflation-protected (TIPS)", "Plain English": "Principal adjusts with inflation prints."},
        {"Class": "International bonds (hedged)", "Plain English": "Foreign bond exposure with currency hedges."},
        {"Class": "Emerging markets debt", "Plain English": "Government/corporate debt in EM — yield & risk."},
        {"Class": "Bank loans / floating rate", "Plain English": "Income that resets with short rates — credit risk remains."},
        {"Class": "Preferred stocks", "Plain English": "Hybrid stock/bond pay income like bonds."},
        {"Class": "Commodities", "Plain English": "Raw materials basket — inflation diversifier."},
        {"Class": "Cash / ultra-short", "Plain English": "Stability & spending buffer."},
        {"Class": "US dividend tilt", "Plain English": "Income-tilt equity sleeve — used in income variants."},
        {"Class": "Municipal bonds (tax-exempt)", "Plain English": "Federal income tax-free yield — state rules vary."},
        {"Class": "Socially screened equity", "Plain English": "ESG / values tilt where offered."},
        {"Class": "Inflation-sensitive assets", "Plain English": "Blend of real assets / TIPS sleeves."},
        {"Class": "International small-cap", "Plain English": "Non-US smaller companies — diversification beyond large-cap ADRs."},
    ]


def customizable_portfolio_story() -> dict[str, Any]:
    return {
        "customization": "Schwab Intelligent Portfolios — **customizable** variants (story)",
        "options": [
            "**Lower cash** sleeve vs default glidepath",
            "**Income-focused** sleeve weights",
            "**Socially responsible** sleeve where available",
            "**Exclude** specific ETFs — engine substitutes **correlated replacement** (story)",
        ],
        "constraints": "Substitutions must preserve diversification & tracking — not unlimited single-stock picks.",
    }


def us_focused_variant_story() -> dict[str, Any]:
    return {
        "name": "U.S.-Focused Strategy Option",
        "shift": "Reduce or **zero out** emerging markets & international equities vs baseline SIP mix",
        "audience": "Investors who prefer **US-domiciled** exposure — still diversified across US sizes/styles",
        "tradeoff": "Less geographic diversification — concentration in US economic cycle (story).",
    }


def income_focused_variant_story() -> dict[str, Any]:
    return {
        "name": "Income-Focused Strategy Option",
        "emphasis": "Dividend equities, **preferred** stocks, **bank loans**, **high-yield** bonds — higher cash flows",
        "tradeoff": "Typically **lower long-term growth** vs growth-tilt portfolios — fits withdrawal-phase investors (story)",
        "fit": "Clients prioritizing **distributions** over aggressive appreciation.",
    }


def municipal_bond_variant_story() -> dict[str, Any]:
    return {
        "name": "Municipal Bond Option (Tax-Efficient)",
        "mechanic": "Swap part of taxable fixed income for **federally tax-exempt** municipal bonds where eligible",
        "state_story": "**State** tax exemption may apply for in-state munis — rules vary (story)",
        "fit": "Higher **marginal brackets** in **taxable** SIP accounts — not primary choice for IRAs",
        "yield_note": "Tax-equivalent yield often compares favorably vs taxable bonds — calculator in platform (story).",
    }


def mock_estimated_tax_savings_ytd(seed_usd: float = 1250.0) -> dict[str, Any]:
    return {
        "estimated_tax_alpha_story_usd": seed_usd,
        "disclaimer": "Illustrative reduction in tax liability from harvested losses — actual savings depend on brackets & IRS rules.",
        "report_period": f"YTD through {date.today().isoformat()}",
    }


def investor_profile_review_story() -> dict[str, Any]:
    return {
        "feature": "Investor Profile Review",
        "cadence": "**Annual** prompt to revisit the risk questionnaire — job change, marriage, horizon shift, etc. (story)",
        "system_behavior": (
            "If answers change **materially**, engine proposes a **new target allocation** with rationale "
            "(plain language + comparison chart)."
        ),
        "user_control": (
            "Client **confirms** adoption of the new target (schedules rebalance) or **rejects** and keeps "
            "prior targets until next review / voluntary edit."
        ),
        "material_change_hint": f"Often flagged when equity mix shifts ~**{int(REBALANCE_DRIFT_THRESHOLD * 100)}%+** vs prior target bands — policy varies (story).",
    }


def equity_share(weights: dict[str, float]) -> float:
    eq_keys = ("US equity", "International equity", "Emerging markets", "Real estate (REITs)")
    return sum(float(weights.get(k, 0.0)) for k in eq_keys)


def profile_change_is_material(
    old_weights: dict[str, float],
    new_weights: dict[str, float],
    threshold: float = 0.05,
) -> tuple[bool, float]:
    """Compare aggregate equity exposure as a simple materiality signal."""
    d = abs(equity_share(old_weights) - equity_share(new_weights))
    return d >= threshold, d


SIP_PREMIUM_SETUP_FEE = 300
SIP_PREMIUM_MONTHLY = 30
SIP_PREMIUM_MINIMUM_USD = 25_000


def sip_premium_story() -> dict[str, Any]:
    return {
        "program": "Schwab Intelligent Portfolios Premium",
        "fees": {
            "one_time_setup_usd": SIP_PREMIUM_SETUP_FEE,
            "monthly_program_usd": SIP_PREMIUM_MONTHLY,
        },
        "minimum_open_usd": SIP_PREMIUM_MINIMUM_USD,
        "advice": "Unlimited access to a **Certified Financial Planner (CFP®)** professional by **phone or video** (story)",
        "planning": "Comprehensive **financial plan** built and **maintained** — updates as goals/taxes change (story)",
        "vs_base": "Adds human planning layer on top of SIP automation — fees separate from ETF expense ratios.",
    }


SPI_MINIMUM_USD = 100_000


def schwab_personalized_indexing_story() -> dict[str, Any]:
    return {
        "program": "Schwab Personalized Indexing (SPI)",
        "minimum_aum_story": f"${SPI_MINIMUM_USD:,}+",
        "mechanic": (
            "**Direct indexing** — holds **individual stocks** that compose a benchmark index rather than a single ETF wrapper."
        ),
        "tax_alpha": "**Stock-level** tax-loss harvesting — swap individual losers while tracking index factor exposure (story)",
        "customization": [
            "Exclude **sectors** or names (concentration / values)",
            "Apply **ESG** or values-based screens",
            "Substitute correlated names where exclusion breaks tracking error budgets",
        ],
        "tradeoffs": "Higher complexity, potentially lower ETF simplicity — suitability & monitoring disclosures apply.",
    }
