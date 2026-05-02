"""
Schwab Bank & cash features — Add-ons only.
"""

from __future__ import annotations

import streamlit as st

from schwab_banking_sim import (
    FDIC_LIMIT_PER_CATEGORY_STORY,
    bill_pay_and_transfers_story,
    fdic_sweep_intelligent_portfolios_story,
    high_yield_investor_checking_story,
    investor_savings_story,
    mobile_check_deposit_story,
    one_interest_brokerage_sweep_story,
)


def render_schwab_banking_addons() -> None:
    st.markdown("### Schwab Bank & cash *(simulation)*")
    st.caption(
        f"APYs and limits are **illustrative** — FDIC standard deposit insurance often cited at **${FDIC_LIMIT_PER_CATEGORY_STORY:,}** per category."
    )

    with st.expander("High Yield Investor Checking", expanded=True):
        st.json(high_yield_investor_checking_story())

    with st.expander("Investor Savings — linked to brokerage", expanded=False):
        apy = st.slider("Illustrative savings APY % (story)", 2.0, 5.5, 3.45, 0.05)
        st.json(investor_savings_story(apy))

    with st.expander("Schwab One® Interest — brokerage cash sweep", expanded=False):
        sw = st.slider("Illustrative sweep yield % (story)", 0.5, 4.0, 2.1, 0.05)
        st.json(one_interest_brokerage_sweep_story(sw))

    with st.expander("Mobile check deposit", expanded=False):
        st.json(mobile_check_deposit_story())

    with st.expander("Bill Pay & transfers", expanded=False):
        st.json(bill_pay_and_transfers_story())

    with st.expander("FDIC sweep — Intelligent Portfolios cash", expanded=False):
        st.json(fdic_sweep_intelligent_portfolios_story())
