"""
Plain-language portfolio helpers for beginner-friendly recommendations.
No Greek letters — logic is documented for transparency in the UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


# Broad buckets we use everywhere (novice-friendly labels)
BUCKET_LABELS = {
    "growth": "Growth (stocks & equity funds)",
    "balanced": "Balanced & income funds",
    "stable": "Stable & short-term (bonds, cash-like)",
}

# Plain-language stress model: when “the market” drops, each bucket responds differently.
# Not a forecast — a transparent teaching assumption for what-if math.
BUCKET_MARKET_SENSITIVITY = {
    "growth": 1.0,
    "balanced": 0.45,
    "stable": 0.08,
}


def bucket_for_holding(asset_type: str, category: str) -> str:
    """Map user-chosen tags to allocation buckets."""
    t = (asset_type or "").lower()
    c = (category or "").lower()
    if t == "stock" or "equity" in c:
        return "growth"
    if "bond" in c or "debt" in c or "fixed" in c:
        return "stable"
    if "balanced" in c or "hybrid" in c:
        return "balanced"
    if t == "mutual_fund":
        return "balanced"
    return "growth"


@dataclass
class RiskProfile:
    """Derived from guided onboarding — no technical ratios."""

    label: str
    growth_target_pct: float  # 0-100
    balanced_target_pct: float
    stable_target_pct: float
    max_drop_comfort: str  # display string


def profile_from_onboarding(answers: dict[str, Any]) -> RiskProfile:
    """
    Convert plain-language answers into target allocation bands.
    """
    horizon = answers.get("horizon", "5–10 years")
    comfort = answers.get("comfort", "A moderate dip (around 15%) is stressful but okay")
    goal = answers.get("goal", "Grow wealth over time")

    # Base tilt from time horizon
    if horizon in ("Less than 3 years",):
        g, b, s = 35.0, 25.0, 40.0
        label = "Cautious — shorter timeline"
    elif horizon in ("3–5 years",):
        g, b, s = 50.0, 30.0, 20.0
        label = "Steady — medium timeline"
    elif horizon in ("5–10 years",):
        g, b, s = 65.0, 25.0, 10.0
        label = "Balanced growth"
    else:
        g, b, s = 75.0, 20.0, 5.0
        label = "Long runway — growth-focused"

    # Adjust for emotional comfort with drops
    if "10%" in comfort or "can't sleep" in comfort.lower():
        g -= 15
        s += 15
        label += " · prefers smaller swings"
    elif "25%" in comfort or "30%" in comfort:
        g += 5
        s -= 5
        label += " · comfortable with volatility"

    # Goal nudge
    if "Preserve" in goal or "Emergency" in goal:
        g -= 10
        s += 10
    if "Big purchase" in goal and horizon.startswith("Less"):
        s += 10
        g -= 10

    # Normalize to 100
    total = g + b + s
    g, b, s = 100 * g / total, 100 * b / total, 100 * s / total

    return RiskProfile(
        label=label,
        growth_target_pct=g,
        balanced_target_pct=b,
        stable_target_pct=s,
        max_drop_comfort=comfort,
    )


def holdings_to_buckets(holdings: list[dict]) -> dict[str, float]:
    totals = {"growth": 0.0, "balanced": 0.0, "stable": 0.0}
    for h in holdings:
        v = float(h.get("value", 0) or 0)
        if v <= 0:
            continue
        b = bucket_for_holding(h.get("type", ""), h.get("category", ""))
        totals[b] += v
    return totals


def portfolio_total(holdings: list[dict]) -> float:
    return sum(float(h.get("value", 0) or 0) for h in holdings)


def stress_test_portfolio(
    holdings: list[dict],
    equity_market_drop_pct: float,
) -> dict[str, Any]:
    """
    Estimate portfolio dollar change if broad equities drop by equity_market_drop_pct.
    Each bucket uses BUCKET_MARKET_SENSITIVITY so beginners see “how bad could it feel”
    without needing correlation matrices.
    """
    buckets = holdings_to_buckets(holdings)
    total_before = portfolio_total(holdings)
    if total_before <= 0:
        return {
            "total_before": 0.0,
            "total_after": 0.0,
            "dollar_change": 0.0,
            "pct_change": 0.0,
            "by_bucket_before": dict(buckets),
            "by_bucket_after": {k: 0.0 for k in buckets},
        }

    m = max(0.0, min(90.0, float(equity_market_drop_pct)))
    drop_frac = m / 100.0
    after: dict[str, float] = {}
    for k, dollars in buckets.items():
        sens = BUCKET_MARKET_SENSITIVITY.get(k, 0.5)
        loss_frac = drop_frac * sens
        after[k] = dollars * (1.0 - loss_frac)
    total_after = sum(after.values())
    dollar_change = total_after - total_before
    pct_change = 100.0 * dollar_change / total_before if total_before else 0.0
    return {
        "total_before": total_before,
        "total_after": total_after,
        "dollar_change": dollar_change,
        "pct_change": pct_change,
        "by_bucket_before": dict(buckets),
        "by_bucket_after": after,
        "assumed_equity_drop_pct": m,
    }


def annual_fee_drag(total_value: float, weighted_expense_pct: float) -> float:
    """Rough yearly cost = balance × expense ratio (as a percent)."""
    if total_value <= 0:
        return 0.0
    return total_value * max(0.0, float(weighted_expense_pct)) / 100.0


def allocation_pcts(holdings: list[dict]) -> dict[str, float]:
    t = portfolio_total(holdings)
    if t <= 0:
        return {"growth": 0.0, "balanced": 0.0, "stable": 0.0}
    buckets = holdings_to_buckets(holdings)
    return {k: 100.0 * buckets[k] / t for k in buckets}


def health_score(
    holdings: list[dict],
    profile: RiskProfile | None,
) -> tuple[int, str]:
    """
    Simple 0-100 score: diversification + distance from target mix.
    """
    t = portfolio_total(holdings)
    if t <= 0 or not holdings:
        return 0, "Add a few holdings to see your portfolio health."

    buckets = holdings_to_buckets(holdings)
    non_empty = sum(1 for v in buckets.values() if v > 0)
    div_score = min(40, 10 * non_empty + (10 if len(holdings) >= 3 else 0))

    if profile is None:
        return min(100, 40 + div_score), "Set your goals in **Guided setup** for a full health check."

    current = allocation_pcts(holdings)
    # penalty for drift from target
    drift = (
        abs(current["growth"] - profile.growth_target_pct)
        + abs(current["balanced"] - profile.balanced_target_pct)
        + abs(current["stable"] - profile.stable_target_pct)
    )
    alignment = max(0, 60 - drift / 2)
    score = int(min(100, div_score + alignment))
    if score >= 75:
        msg = "Your mix is reasonably aligned with your stated comfort and timeline."
    elif score >= 55:
        msg = "You're on the right track; small tweaks could bring you closer to your target mix."
    else:
        msg = "Your current mix may feel stressful if markets move; consider rebalancing toward your target."
    return score, msg


SCENARIOS = [
    {
        "id": "market_drop",
        "title": "What if the market drops about 20%?",
        "blurb": "Stocks often fall more than bonds during shocks. We suggest shifting toward stability—not timing the market, but matching your need for peace of mind.",
    },
    {
        "id": "inflation",
        "title": "What if inflation stays high for a while?",
        "blurb": "Cash loses purchasing power when prices rise. A modest tilt toward growth assets (within your comfort) can help long-term; keep near-term expenses in stable holdings.",
    },
    {
        "id": "withdraw",
        "title": "What if I need to withdraw 20% next year?",
        "blurb": "Money you need soon should sit in stable, easy-to-access choices so you aren't forced to sell growth holdings during a dip.",
    },
    {
        "id": "volatile",
        "title": "What if I want less day-to-day stress?",
        "blurb": "Lowering swings usually means more stable and balanced funds, even if long-term growth might be a bit slower.",
    },
]


def recommend_for_scenario(
    scenario_id: str,
    holdings: list[dict],
    profile: RiskProfile | None,
    *,
    equity_shock_pct: float = 20.0,
) -> dict[str, Any]:
    """Returns structured recommendation for UI transparency."""
    prof = profile or profile_from_onboarding(
        {
            "horizon": "5–10 years",
            "comfort": "A moderate dip (around 15%) is stressful but okay",
            "goal": "Grow wealth over time",
        }
    )
    target_g = prof.growth_target_pct
    total = portfolio_total(holdings)

    actions: list[str] = []
    rationale: list[str] = []
    costs_note = (
        "Mutual funds may charge an expense ratio yearly (shown in your factsheet). "
        "Buying/selling may trigger brokerage fees if your platform charges them — check your broker."
    )
    tax_note = (
        "Selling investments outside tax-advantaged accounts may trigger capital gains tax in your country. "
        "This prototype cannot calculate your exact tax; consider speaking to a tax advisor for large moves."
    )

    shift_pp = 0.0
    dollar_hint: str | None = None

    if scenario_id == "market_drop":
        shift_s = 10.0
        shift_pp = shift_s
        actions.append(
            f"Consider moving about **{shift_s:.0f} percentage points** of your whole portfolio from growth toward stable holdings "
            f"(e.g., short-term debt or cash-like funds), bringing growth closer to **{max(target_g - 10, 0):.0f}%** of your target mix."
        )
        if total > 0:
            approx_d = total * (shift_s / 100.0)
            dollar_hint = (
                f"Ballpark trade size to discuss with your broker: about **${approx_d:,.0f}** "
                f"moving from growth-style to stable-style (equals {shift_s:.0f}% of your ${total:,.0f} total)."
            )
        rationale.append(
            "After a large drop, having enough stable assets reduces the chance you'll sell growth holdings at a bad time out of fear."
        )
        rationale.append(
            "This is a risk-management move, not a prediction that markets will keep falling."
        )
        rationale.append(
            f"We stress-tested a **{equity_shock_pct:.0f}%** decline in broad equities using simple bucket sensitivities "
            "(growth moves most, stable least) — see **How this math works** below."
        )
    elif scenario_id == "inflation":
        actions.append(
            "Keep money you'll spend within 1–2 years in **stable** holdings; aim to keep **long-term** savings tilted toward growth within your comfort zone."
        )
        rationale.append(
            "High inflation erodes cash; growth assets have historically helped long-term investors keep pace, but they bounce around more in the short run."
        )
    elif scenario_id == "withdraw":
        shift_pp = 20.0
        actions.append(
            f"Move roughly **20% of your portfolio** into stable, liquid options ahead of your withdrawal date."
        )
        if total > 0:
            w = total * 0.20
            dollar_hint = (
                f"Rough amount to park in stable, easy-to-access choices before you need it: about **${w:,.0f}** "
                f"(20% of ${total:,.0f})."
            )
        rationale.append(
            "That way you won't be forced to sell stock funds during a possible downturn when you need the money."
        )
    else:  # volatile / stress
        shift_pp = 12.5
        actions.append(
            f"Gradually shift about **10–15 percentage points** from growth toward balanced and stable until daily swings feel manageable."
        )
        if total > 0:
            approx_d = total * (shift_pp / 100.0)
            dollar_hint = (
                f"Using the midpoint (**~12.5** percentage points of your total), that's roughly **${approx_d:,.0f}** "
                f"to shift over time — not all at once unless your platform allows free exchanges."
            )
        rationale.append(
            "This aligns your investments with how much uncertainty you can tolerate emotionally—not a judgment about your goals."
        )

    # Generic transparency line
    rationale.append(
        f"Your stated comfort with drops: “{prof.max_drop_comfort}”. Recommendations respect that framing."
    )

    shock = stress_test_portfolio(holdings, equity_shock_pct)

    return {
        "actions": actions,
        "rationale": rationale,
        "costs_note": costs_note,
        "tax_note": tax_note,
        "profile_label": prof.label,
        "dollar_hint": dollar_hint,
        "shift_pp": shift_pp,
        "stress": shock,
        "equity_shock_pct": equity_shock_pct,
    }


def allocation_df(holdings: list[dict], profile: RiskProfile | None) -> pd.DataFrame:
    cur = allocation_pcts(holdings)
    rows = []
    for key in ["growth", "balanced", "stable"]:
        row = {
            "Bucket": BUCKET_LABELS[key],
            "Your portfolio %": round(cur[key], 1),
        }
        if profile:
            tgt = getattr(profile, f"{key}_target_pct")
            row["Target mix %"] = round(tgt, 1)
        rows.append(row)
    return pd.DataFrame(rows)
