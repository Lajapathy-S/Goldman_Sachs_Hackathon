"""
Schwab wealth advisory & planning tools — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from retirement_planning_sim import (
    college_529_goal_tracker,
    state_529_catalog,
    state_tax_benefit_estimate,
)
from schwab_wealth_sim import (
    ALT_INVESTMENTS_MIN_USD,
    WEALTH_ADVISORY_MIN_USD,
    alternative_investments_select_story,
    college_savings_center_intro_story,
    estate_planning_visualization_story,
    financial_plan_sip_premium_detail_story,
    forge_global_private_markets_story,
    monte_carlo_retirement_probability_score,
    pledged_asset_line_story,
    schwab_advisor_network_story,
    schwab_wealth_advisory_story,
    social_security_optimizer_comparison,
    trust_family_organization_accounts_story,
)


def render_schwab_wealth_addons() -> None:
    st.markdown("### Schwab wealth & planning *(simulation)*")
    st.caption("Minimums, launches, and integrations follow your **spec narrative** — not live Schwab policies.")

    with st.expander(f"Schwab Wealth Advisory — HNW (${WEALTH_ADVISORY_MIN_USD:,}+ story)", expanded=True):
        st.json(schwab_wealth_advisory_story())

    with st.expander("Schwab Advisor Network — RIA referrals", expanded=False):
        st.json(schwab_advisor_network_story())

    with st.expander("Estate Planning Visualization — Wealth.com integration (2025 story)", expanded=False):
        st.json(estate_planning_visualization_story())

    with st.expander("Trust, family & organization accounts", expanded=False):
        st.json(trust_family_organization_accounts_story())

    with st.expander(f"Alternative Investments Select (${ALT_INVESTMENTS_MIN_USD:,}+ · 2025 story)", expanded=False):
        st.json(alternative_investments_select_story())

    with st.expander("Forge Global — private markets (2025 acquisition story)", expanded=False):
        st.json(forge_global_private_markets_story())

    with st.expander("Pledged Asset Line (PAL)", expanded=False):
        idx = st.slider("Illustrative reference rate % (story)", 5.0, 12.0, 8.25, 0.05)
        st.json(pledged_asset_line_story(idx))

    with st.expander("Financial Plan — SIP Premium (CFP written plan)", expanded=False):
        st.json(financial_plan_sip_premium_detail_story())

    with st.expander("Retirement Income Projector — Monte Carlo probability score", expanded=False):
        st.markdown(
            "Probability **0–100** that simplified draws last through the horizon — **toy** model for coursework."
        )
        r1, r2, r3 = st.columns(3)
        with r1:
            nest = st.number_input("Investable portfolio ($)", value=1_200_000.0, step=50_000.0)
            need = st.number_input("Annual expenses before SS ($)", value=85_000.0, step=5000.0)
            ss = st.number_input("Annual Social Security ($)", value=42_000.0, step=1000.0)
        with r2:
            yrs = st.number_input("Retirement horizon (years)", value=28, min_value=5, max_value=50)
            er = st.number_input("Expected return %", value=5.5, step=0.5)
            vol = st.number_input("Volatility %", value=12.0, step=0.5)
        with r3:
            inf = st.number_input("Expense inflation %", value=2.5, step=0.1)
        mc = monte_carlo_retirement_probability_score(
            nest, need, int(yrs), ss, er, vol, inf,
        )
        st.metric("Probability score (0–100)", mc["probability_score_0_100"])
        st.json({k: v for k, v in mc.items() if k != "probability_score_0_100"})

    with st.expander("Social Security Optimizer — claiming scenarios", expanded=False):
        st.markdown(
            "Compare **early (62)**, **full retirement age (67)**, and **delayed (70)** — "
            "cumulative lifetime benefits are **undiscounted** teaching projections."
        )
        o1, o2 = st.columns(2)
        with o1:
            pia = st.number_input(
                "Primary Insurance Amount (PIA) at 67 — monthly ($)",
                value=3_200.0,
                step=50.0,
                key="ss_pia",
            )
        with o2:
            end_age = st.number_input(
                "Planning end age (longevity assumption)",
                value=88.0,
                min_value=70.0,
                max_value=105.0,
                step=0.5,
                key="ss_end",
            )
        ss_out = social_security_optimizer_comparison(pia, end_age)
        df_ss = pd.DataFrame(ss_out["scenarios"])
        st.dataframe(df_ss, use_container_width=True, hide_index=True)
        ch = df_ss.set_index("Scenario")["Cumulative lifetime ($)"]
        st.bar_chart(ch)
        st.caption(
            f"**Illustrative winner by cumulative total:** {ss_out.get('largest_cumulative_story') or '—'} "
            "(longevity dominates — not advice)."
        )
        st.json({k: v for k, v in ss_out.items() if k != "scenarios"})

    with st.expander("College Savings Center — 529 plans", expanded=False):
        st.json(college_savings_center_intro_story())
        st.dataframe(pd.DataFrame(state_529_catalog()), use_container_width=True, hide_index=True)
        g1, g2 = st.columns(2)
        with g1:
            cb = st.number_input("529 balance ($)", value=32_000.0, key="w529bal")
            mc2 = st.number_input("Monthly contribution ($)", value=500.0, key="w529m")
            yl = st.number_input("Years to college", value=9.0, step=0.5, key="w529y")
        with g2:
            ar = st.number_input("Annual return %", value=5.0, step=0.5, key="w529r")
            c1y = st.number_input("First-year cost estimate ($)", value=38_000.0, step=1000.0, key="w529c")
        st.json(college_529_goal_tracker(cb, mc2, yl, ar, c1y))
        st.markdown("**State tax benefit (story)**")
        stx = st.selectbox("State", [r["State"] for r in state_529_catalog()], key="w529st")
        contrib = st.number_input("Annual 529 contribution ($)", value=10_000.0, key="w529contrib")
        marg = st.slider("Marginal state rate %", 0.0, 12.0, 6.0, key="w529marg")
        st.json(state_tax_benefit_estimate(stx, contrib, marg))
