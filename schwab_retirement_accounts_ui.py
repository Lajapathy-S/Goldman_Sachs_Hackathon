"""
Schwab retirement & account types — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from retirement_planning_sim import (
    college_529_goal_tracker,
    rmd_amount,
    state_529_catalog,
)
from schwab_retirement_accounts_sim import (
    NERDWALLET_IRA_RANK_STORY,
    schwab_529_alliance_story,
    schwab_charitable_daf_story,
    schwab_custodial_accounts_story,
    schwab_employer_401k_services_story,
    schwab_rollover_ira_story,
    schwab_small_business_retirement_story,
    schwab_traditional_roth_ira_story,
)


def render_schwab_retirement_accounts_addons() -> None:
    st.markdown("### Schwab retirement & accounts *(simulation)*")
    st.caption(f"Recognition line: {NERDWALLET_IRA_RANK_STORY}")

    with st.expander("Traditional & Roth IRA", expanded=True):
        st.json(schwab_traditional_roth_ira_story())
        st.markdown("**RMD calculator (illustrative)** — shared teaching stub")
        c1, c2 = st.columns(2)
        with c1:
            bal = st.number_input("Traditional IRA balance ($)", value=420_000.0, key="schwab_ira_bal")
        with c2:
            age_r = st.number_input("Age", value=74, min_value=25, max_value=100, key="schwab_ira_age")
        st.json(rmd_amount(bal, int(age_r)))

    with st.expander("Rollover IRA", expanded=False):
        st.json(schwab_rollover_ira_story())

    with st.expander("Small business retirement (SEP, SIMPLE, Individual 401(k))", expanded=False):
        st.json(schwab_small_business_retirement_story())

    with st.expander("401(k) employer plans & employee portal", expanded=False):
        st.json(schwab_employer_401k_services_story())

    with st.expander("Custodial accounts (UGMA/UTMA)", expanded=False):
        st.json(schwab_custodial_accounts_story())

    with st.expander("Charitable accounts — Donor-Advised Fund (Schwab Charitable)", expanded=False):
        st.json(schwab_charitable_daf_story())

    with st.expander("529 college savings — alliance & goal tracker", expanded=False):
        st.json(schwab_529_alliance_story())
        st.dataframe(pd.DataFrame(state_529_catalog()), use_container_width=True, hide_index=True)
        g1, g2 = st.columns(2)
        with g1:
            cb = st.number_input("529 balance ($)", value=22_000.0, key="schwab529b")
            mc = st.number_input("Monthly contribution ($)", value=450.0, key="schwab529m")
            yl = st.number_input("Years to enrollment", value=11.0, step=0.5, key="schwab529y")
        with g2:
            ar = st.number_input("Annual return %", value=5.25, step=0.25, key="schwab529r")
            cy = st.number_input("First-year college cost ($)", value=36_000.0, step=1000.0, key="schwab529c")
        st.json(college_529_goal_tracker(cb, mc, yl, ar, cy))
