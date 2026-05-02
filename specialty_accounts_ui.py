"""
HSA, Youth, Trust, Custodial — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from specialty_accounts_sim import (
    HSA_LIMIT_FAMILY_STORY,
    HSA_LIMIT_INDIVIDUAL_STORY,
    QUALIFIED_EXPENSE_LABELS,
    custodial_account_snapshot,
    hsa_contribution_room,
    hsa_tax_benefit_estimate,
    mock_qualified_expenses_ledger,
    trust_account_overview,
    youth_account_profile,
)


def render_specialty_accounts_addons() -> None:
    st.markdown("### Specialty accounts *(simulation)*")
    st.caption("HSA limits, trust law, and custodial termination ages are **illustrative** — verify with plan docs and counsel.")

    # HSA
    with st.expander("HSA — investments, contributions, expenses, tax benefit", expanded=False):
        st.markdown(
            f"Investment-eligible HSA with **Fidelity** funds/ETFs when offered (story). "
            f"Illustrative caps: **individual ${HSA_LIMIT_INDIVIDUAL_STORY:,}**, "
            f"**family ${HSA_LIMIT_FAMILY_STORY:,}** (+ catch-up story)."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            cov = st.selectbox("Coverage tier", ["individual", "family"])
        with c2:
            age_h = st.number_input("Your age", min_value=0, max_value=120, value=38, key="hsa_age")
        with c3:
            ytd = st.number_input("Contributed YTD ($)", value=2100.0, step=100.0, key="hsa_ytd")
        st.json(hsa_contribution_room(cov, int(age_h), ytd))
        st.markdown("**Qualified expense categories (reference)**")
        for q in QUALIFIED_EXPENSE_LABELS:
            st.markdown(f"- {q}")
        st.markdown("**Sample ledger — categorization (sim)**")
        st.dataframe(pd.DataFrame(mock_qualified_expenses_ledger()), use_container_width=True, hide_index=True)
        st.markdown("**Tax benefit calculator (story)**")
        t1, t2, t3, t4 = st.columns(4)
        with t1:
            pay = st.number_input("Payroll contribution ($)", value=3500.0, key="hsa_pay")
        with t2:
            er = st.number_input("Employer contribution ($)", value=750.0, key="hsa_er")
        with t3:
            mf = st.slider("Marginal federal %", 0.0, 37.0, 22.0)
        with t4:
            ms = st.slider("Marginal state %", 0.0, 13.0, 5.0)
        st.json(hsa_tax_benefit_estimate(pay, er, mf, ms))

    # Youth
    with st.expander("Youth Account — teens 13–17", expanded=False):
        ya = st.number_input("Teen age", min_value=10, max_value=22, value=15, key="youth_age")
        prof = youth_account_profile(int(ya))
        if prof["eligible"]:
            st.success(prof["message"])
        else:
            st.warning(prof["message"])
        st.markdown(f"**Minimum:** ${prof['minimum']} · **Products:** {', '.join(prof['products'])}")
        st.write(prof["parental_oversight"])
        st.markdown("**Education modules tailored for teens**")
        for m in prof["education_modules"]:
            st.markdown(f"- {m}")

    # Trust
    with st.expander("Trust accounts — trustee tools & estate center", expanded=False):
        tt = st.radio("Trust type", ["Revocable living trust", "Irrevocable trust"], horizontal=True)
        ov = trust_account_overview(tt)
        st.markdown(f"**Registration:** {ov['trust_type_story']}")
        st.markdown("**Trustee management tools**")
        for x in ov["trustee_tools"]:
            st.markdown(f"- {x}")
        st.markdown("**Estate planning center**")
        for x in ov["estate_center"]:
            st.markdown(f"- {x}")
        st.markdown("**Beneficiary designation review — prompts**")
        for x in ov["beneficiary_review_prompts"]:
            st.markdown(f"- {x}")

    # Custodial
    with st.expander("Custodial accounts (UGMA / UTMA)", expanded=False):
        f1, f2, f3, f4 = st.columns(4)
        with f1:
            flavor = st.selectbox("Account type", ["UTMA", "UGMA"])
        with f2:
            min_age = st.number_input("Minor age", min_value=0, max_value=25, value=16)
        with f3:
            st_ab = st.selectbox("State", ["CA", "NY", "TX", "FL", "PA"])
        with f4:
            bal_c = st.number_input("Account balance ($)", value=12_500.0, step=500.0)
        snap = custodial_account_snapshot(flavor, int(min_age), st_ab, bal_c)
        st.json(snap)
        if snap["transfer_at_majority_flag"]:
            st.info(
                "**Transfer alert:** approaching or at age of majority — termination & registration change flagged for custodian (story)."
            )
