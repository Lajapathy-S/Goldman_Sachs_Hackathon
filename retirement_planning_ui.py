"""
§2.6 Retirement planning & account types — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from retirement_planning_sim import (
    PLANS_ADMINISTERED_STORY,
    backdoor_roth_steps,
    college_529_goal_tracker,
    employer_401k_view,
    rollover_ira_info,
    roth_contribution_eligibility,
    roth_tax_free_growth,
    rmd_amount,
    sep_simple_snapshot,
    state_529_catalog,
    state_tax_benefit_estimate,
    traditional_ira_snapshot,
)


def render_retirement_planning_addons() -> None:
    st.markdown("### Retirement planning & account types *(§2.6 simulation)*")
    st.caption(
        "Contribution limits, phase-outs, and tax outcomes are **illustrative** — not tax or legal advice."
    )
    rp_age = st.number_input(
        "Age (used in calculators below)", min_value=18, max_value=105, value=42, key="rp_age"
    )

    # Traditional IRA
    with st.expander("Traditional IRA — contributions, deductibility, RMD, rollovers", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            magi_t = st.number_input("Est. MAGI ($)", value=95000.0, step=1000.0)
        with c2:
            covered = st.checkbox("Covered by workplace retirement plan", value=True)
        cy = st.number_input("Contributed YTD ($)", value=3500.0, step=500.0)
        lim_story = st.number_input("Annual contribution limit — story ($)", value=7000.0, step=500.0)
        snap = traditional_ira_snapshot(cy, lim_story, int(rp_age), magi_t, covered)
        st.json({k: v for k, v in snap.items() if k != "rollover_support"})
        st.write("**Rollover:**", snap["rollover_support"])
        st.success(
            "**Fidelity ZERO & other funds:** Traditional IRA can hold ZERO expense-ratio funds when offered (story)."
        )
        bal_rmd = st.number_input("Traditional IRA balance for RMD check ($)", value=580_000.0, step=10000.0)
        st.json(rmd_amount(bal_rmd, int(rp_age)))

    # Roth IRA
    with st.expander("Roth IRA — income limits, deadlines, growth calculator, backdoor", expanded=False):
        rc1, rc2 = st.columns(2)
        with rc1:
            magi_r = st.number_input("Est. MAGI for Roth ($)", value=185000.0, step=1000.0, key="roth_magi")
        with rc2:
            filing = st.selectbox("Filing status", ["single", "married filing jointly"], key="roth_file")
        elig = roth_contribution_eligibility(magi_r, filing, int(rp_age))
        st.json(elig)
        st.caption(elig["deadline_note"])
        st.markdown("**Backdoor Roth — step overview (story)**")
        for i, step in enumerate(backdoor_roth_steps(), start=1):
            st.markdown(f"{i}. {step}")
        g1, g2, g3, g4 = st.columns(4)
        with g1:
            rb = st.number_input("Current Roth balance ($)", value=42000.0, key="rb")
        with g2:
            ann = st.number_input("Annual contribution ($)", value=7000.0, key="rac")
        with g3:
            yrs = st.number_input("Years invested", value=20.0, step=1.0, key="ry")
        with g4:
            ret = st.number_input("Assumed return %", value=6.5, step=0.5, key="rr")
        st.json(roth_tax_free_growth(rb, ann, yrs, ret))

    # Rollover IRA
    with st.expander("Rollover IRA — 401(k) / 403(b) guidance", expanded=False):
        info = rollover_ira_info()
        st.markdown(f"**Support:** {info['support_team']}")
        st.write("**Sources:**", ", ".join(info["sources"]))
        st.markdown(f"**Direct rollover:** {info['direct_rollover']}")
        st.markdown(f"**60-day rollover:** {info['sixty_day']}")
        st.markdown("**Checklist**")
        for x in info["checklist"]:
            st.markdown(f"- {x}")

    # SEP / SIMPLE
    with st.expander("SEP-IRA & SIMPLE IRA — small business", expanded=False):
        plan_pick = st.radio("Plan type", ["SEP-IRA", "SIMPLE IRA"], horizontal=True)
        emp_n = st.number_input("Number of eligible employees", min_value=0, value=3)
        net_se = st.number_input("Net self-employment earnings ($)", value=140000.0, step=5000.0)
        st.json(sep_simple_snapshot(net_se, int(emp_n), plan_pick))

    # 401(k) administration
    with st.expander(f"401(k) plan administration — **{PLANS_ADMINISTERED_STORY:,}+** employers (story)", expanded=False):
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            bal_401 = st.number_input("Your 401(k) balance ($)", value=112000.0, key="bal401k")
        with k2:
            def_pct = st.number_input("Your deferral %", value=12.0, step=1.0)
        with k3:
            match_pct = st.number_input("Employer match % of salary", value=4.0, step=0.5)
        with k4:
            match_cap = st.number_input("Employer match cap % of salary", value=6.0, step=0.5)
        ev = employer_401k_view(bal_401, def_pct, match_pct, match_cap)
        st.metric("Plans administered (story)", f"{ev['plan_participants_story']:,}")
        m1, m2, m3 = st.columns(3)
        m1.metric("Balance (sim)", f"${ev['your_balance_sim']:,.0f}")
        m2.metric("Fund choices (story)", ev["fund_lineup_count_story"])
        m3.metric("Your deferral ($/yr story)", f"${ev['your_contribution_dollars_story']:,.0f}")
        st.json({k: v for k, v in ev.items() if k not in ("plan_participants_story", "your_balance_sim", "fund_lineup_count_story", "your_contribution_dollars_story")})

    # 529
    with st.expander("529 college savings — state plans, goal tracker, deduction helper", expanded=False):
        st.dataframe(pd.DataFrame(state_529_catalog()), use_container_width=True, hide_index=True)
        st.markdown("**Goal tracker**")
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            cb = st.number_input("529 balance ($)", value=28000.0)
        with s2:
            mc = st.number_input("Monthly contribution ($)", value=400.0)
        with s3:
            yleft = st.number_input("Years to enrollment", value=10.0, step=0.5)
        with s4:
            ar = st.number_input("Annual return %", value=5.5, step=0.5, key="529r")
        cost1 = st.number_input("Estimated first-year college cost ($)", value=35000.0, step=1000.0)
        gt = college_529_goal_tracker(cb, mc, yleft, ar, cost1)
        m1, m2, m3 = st.columns(3)
        m1.metric("Projected at enrollment", f"${gt['projected_balance_at_enrollment']:,.0f}")
        m2.metric("Illustrative need (story)", f"${gt['illustrative_four_year_need_story']:,.0f}")
        m3.metric("Gap (story)", f"${gt['funding_gap_story']:,.0f}")
        st.caption(gt["message"])
        st.markdown("**State tax benefit estimator (story)**")
        stx = st.selectbox("State of residence", [r["State"] for r in state_529_catalog()])
        contrib_529 = st.number_input("Planned annual 529 contribution ($)", value=8000.0, step=500.0)
        marg = st.slider("Marginal state rate % (story)", 0.0, 12.0, 6.0)
        st.json(state_tax_benefit_estimate(stx, contrib_529, marg))
