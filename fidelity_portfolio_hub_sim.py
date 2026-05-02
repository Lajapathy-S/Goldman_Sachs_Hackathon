"""
Fidelity-style portfolio hub — planning, tax, aggregation stories (mock analytics).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from portfolio_logic import RiskProfile, bucket_for_holding, holdings_to_buckets, portfolio_total

# Map core buckets → reporting asset classes (illustrative).
BUCKET_TO_ASSET_CLASS_SPLITS = {
    "growth": {"US equity": 0.62, "International equity": 0.38},
    "balanced": {"US equity": 0.35, "International equity": 0.25, "Fixed income": 0.40},
    "stable": {"Fixed income": 0.65, "Cash & equivalents": 0.35},
}


GOAL_TYPES = ("Retirement", "College", "Home purchase", "Emergency fund")


def target_asset_pct_from_profile(profile: RiskProfile) -> dict[str, float]:
    """Map Goals profile buckets → reporting sleeves (same bridge as BUCKET_TO_ASSET_CLASS_SPLITS)."""
    G = profile.growth_target_pct / 100.0
    B = profile.balanced_target_pct / 100.0
    S = profile.stable_target_pct / 100.0
    return {
        "US equity": G * 0.62 + B * 0.35,
        "International equity": G * 0.38 + B * 0.25,
        "Fixed income": B * 0.40 + S * 0.65,
        "Cash & equivalents": S * 0.35,
    }


def drift_vs_target(profile: RiskProfile | None, holdings: list[dict]) -> pd.DataFrame:
    """Color-coded drift uses labels in UI (On track / Watch / Review)."""
    if profile is None:
        return pd.DataFrame({"Message": ["Set **Goals & profile** to compute target mix."]})
    tgt = target_asset_pct_from_profile(profile)
    act = asset_class_breakdown(holdings)
    if act.empty:
        return pd.DataFrame({"Message": ["Add holdings for actual allocation."]})
    act_map = dict(zip(act["Asset class"], act["% of portfolio"]))
    rows = []
    for acl, tp in tgt.items():
        ap = float(act_map.get(acl, 0.0))
        drift = ap - tp
        ad = abs(drift)
        if ad < 4.0:
            status = "On track"
        elif ad < 10.0:
            status = "Watch"
        else:
            status = "Review"
        rows.append(
            {
                "Asset class": acl,
                "Target %": round(tp, 1),
                "Actual %": round(ap, 1),
                "Drift (pp)": round(drift, 1),
                "Drift status": status,
            }
        )
    return pd.DataFrame(rows)


def gain_loss_report_plaintext(gl_df: pd.DataFrame) -> str:
    return (
        "AIChemist — Realized / Unrealized gain-loss (simulation)\n"
        "Not tax advice. Export for review only.\n\n" + gl_df.to_csv(index=False)
    )


def retirement_savings_adjustment_hint(
    monthly_gap: float,
    years_to_retirement: float,
) -> dict[str, Any]:
    """Toy suggestion when income falls short of need."""
    if monthly_gap <= 0:
        return {"suggested_extra_monthly_save": 0.0, "note": "No monthly shortfall in this snapshot."}
    # heuristic: chip away at gap with incremental savings
    raw = min(monthly_gap * 0.25, monthly_gap)
    years_f = max(1.0, float(years_to_retirement))
    damp = min(1.0, 12.0 / years_f)
    sug = round(raw * damp, 2)
    return {
        "suggested_extra_monthly_save": sug,
        "note": "Illustrative extra savings — meet with a planner for a real plan.",
    }


def asset_class_breakdown(holdings: list[dict]) -> pd.DataFrame:
    buckets = holdings_to_buckets(holdings)
    rows = []
    for bkey, dollars in buckets.items():
        if dollars <= 0:
            continue
        splits = BUCKET_TO_ASSET_CLASS_SPLITS.get(bkey, {})
        for acl, frac in splits.items():
            rows.append({"Asset class": acl, "Amount ($)": dollars * frac})
    if not rows:
        return pd.DataFrame(columns=["Asset class", "Amount ($)", "% of portfolio"])
    df = pd.DataFrame(rows).groupby("Asset class", as_index=False)["Amount ($)"].sum()
    tot = df["Amount ($)"].sum()
    df["% of portfolio"] = (100.0 * df["Amount ($)"] / tot) if tot else 0
    return df.round(2)


def sector_stub_within_equity(holdings: list[dict]) -> pd.DataFrame:
    """Toy sector slice — not real sector tags."""
    eq_value = sum(
        float(h.get("value", 0) or 0)
        for h in holdings
        if bucket_for_holding(h.get("type", ""), h.get("category", "")) in ("growth", "balanced")
    )
    if eq_value <= 0:
        return pd.DataFrame()
    parts = [("Technology", 0.28), ("Healthcare", 0.14), ("Financials", 0.13), ("Consumer", 0.12), ("Other", 0.33)]
    return pd.DataFrame(
        [{"Sector": n, "Approx % of equity sleeve": round(100 * p, 1)} for n, p in parts]
    )


def sector_balance_notes(holdings: list[dict]) -> list[str]:
    """Surface sector sleeve narrative (toy weights)."""
    df = sector_stub_within_equity(holdings)
    if df.empty:
        return []
    top = df.sort_values("Approx % of equity sleeve", ascending=False).iloc[0]
    name = top["Sector"]
    pct = top["Approx % of equity sleeve"]
    notes = [
        f"**Sector sleeve:** largest bucket is **{name}** (~{pct}%). Consider diversification when adding new buys."
    ]
    if pct > 35:
        notes.append("**Imbalance flag:** one sector sleeve exceeds ~35% in this stub — review tech/cyclical tilt.")
    return notes


def concentration_flags(holdings: list[dict]) -> list[str]:
    t = portfolio_total(holdings)
    if t <= 0:
        return ["No positions to analyze."]
    msgs = []
    for h in holdings:
        v = float(h.get("value", 0) or 0)
        if v / t > 0.4:
            msgs.append(f"**Concentration:** “{h.get('name')}” is ~{100 * v / t:.0f}% of portfolio.")
    buckets = holdings_to_buckets(holdings)
    g_pct = 100 * buckets.get("growth", 0) / t
    if g_pct > 75:
        msgs.append(f"**Growth tilt:** ~{g_pct:.0f}% in growth-style holdings — check risk vs goal.")
    if g_pct < 25 and t > 0:
        msgs.append("**Conservative tilt:** low growth allocation vs typical balanced targets.")
    msgs.extend(sector_balance_notes(holdings))
    if not msgs:
        msgs.append("No major concentration flags in this teaching heuristic.")
    return msgs


def monte_carlo_goal_success(
    *,
    goal_wealth: float,
    years: float,
    initial: float,
    monthly_contribution: float,
    annual_return_mean: float = 0.06,
    annual_vol: float = 0.14,
    n_paths: int = 400,
    seed: int = 42,
) -> tuple[float, pd.Series]:
    rng = np.random.default_rng(seed)
    months = max(1, int(years * 12))
    mu_m = (1 + annual_return_mean) ** (1 / 12) - 1
    sig_m = annual_vol / np.sqrt(12)
    success = 0
    end_wealths = []
    for _ in range(n_paths):
        w = float(initial)
        for _m in range(months):
            w = w * (1 + rng.normal(mu_m, sig_m)) + monthly_contribution
        end_wealths.append(w)
        if w >= goal_wealth:
            success += 1
    prob = success / n_paths
    dist = pd.Series(end_wealths)
    return prob, dist


def retirement_monthly_income_story(
    *,
    nest_egg: float,
    withdrawal_rate: float = 0.04,
    social_security_monthly: float = 2200,
    years_in_retirement: float = 25,
) -> dict[str, Any]:
    from_portfolio = nest_egg * (withdrawal_rate / 12) if nest_egg > 0 else 0
    total = from_portfolio + social_security_monthly
    return {
        "nest_egg": nest_egg,
        "withdrawal_rate_annual": withdrawal_rate,
        "from_portfolio_monthly": round(from_portfolio, 2),
        "social_security_monthly": social_security_monthly,
        "total_monthly_estimate": round(total, 2),
        "note": "Static 4%-rule style story + SS — not a personal plan.",
    }


def tax_loss_candidates(holdings: list[dict]) -> pd.DataFrame:
    rows = []
    replacements = ["Broad equity ETF (sim)", "Core bond fund (sim)", "TIP sleeve (sim)"]
    for i, h in enumerate(holdings):
        v = float(h.get("value", 0) or 0)
        cost = float(h.get("cost_basis_total", v * 0.95) or 0)
        unreal = v - cost
        if unreal < -50:  # loss candidate
            rows.append(
                {
                    "Holding": h.get("name"),
                    "Unrealized ($)": round(unreal, 2),
                    "Replacement idea": replacements[i % len(replacements)],
                    "Tax savings (rough, sim)": round(-unreal * 0.22, 2),
                }
            )
    if not rows:
        rows.append(
            {
                "Holding": "(none flagged)",
                "Unrealized ($)": 0,
                "Replacement idea": "—",
                "Tax savings (rough, sim)": 0,
            }
        )
    return pd.DataFrame(rows)


def external_accounts_template() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Source": "Linked checking (Plaid sim)", "Balance": 8200, "Type": "Cash"},
            {"Source": "External brokerage (Yodlee sim)", "Balance": 34000, "Type": "Investments"},
            {"Source": "Mortgage (manual)", "Balance": -285000, "Type": "Liability"},
            {"Source": "Credit card", "Balance": -1200, "Type": "Liability"},
        ]
    )


def gain_loss_table(holdings: list[dict]) -> pd.DataFrame:
    rows = []
    for h in holdings:
        v = float(h.get("value", 0) or 0)
        cost = float(h.get("cost_basis_total", v * 0.97) or 0)
        unreal = v - cost
        term = "LT"
        for lot in h.get("lots") or []:
            if str(lot.get("term", "")).upper() == "ST":
                term = "Mixed"
        rows.append(
            {
                "Name": h.get("name"),
                "Cost basis": round(cost, 2),
                "Value": round(v, 2),
                "Unrealized ($)": round(unreal, 2),
                "Term hint": term,
            }
        )
    return pd.DataFrame(rows)


def tax_center_ytd_mock() -> dict[str, Any]:
    return {
        "Est. taxable dividends (ytd)": 1840,
        "Est. realized gains (ytd)": 420,
        "Est. realized losses (ytd)": -310,
        "1099 status": "Expected Feb (sim)",
        "YTD tax liability est.": 950,
    }


def annual_checkup_items() -> list[tuple[str, str]]:
    return [
        ("Savings rate", "On track vs goal"),
        ("Asset allocation", "Within bands"),
        ("Beneficiaries", "Review IRA/401k"),
        ("Insurance gap", "Life / disability"),
        ("Goal progress", "College / home / retirement"),
    ]
