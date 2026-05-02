"""
Schwab-style extended trading products — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from schwab_extended_sim import (
    MARGIN_BASE_RATE_STORY,
    MUTUAL_FUND_ONESOURCE_COUNT_STORY,
    extended_hours_trading_story,
    international_trading_story,
    ipo_and_new_issues_story,
    margin_account_snapshot,
    mock_ipo_calendar_rows,
    mock_onesource_fund_sample,
    mutual_fund_onesource_summary,
    schwab_crypto_account_story,
)


def render_schwab_extended_addons() -> None:
    st.markdown("### Schwab-style extended products *(simulation)*")
    st.caption("Program names and counts follow your **spec sheet** — not live Schwab data.")

    with st.expander(
        f"Mutual Fund OneSource® — ~{MUTUAL_FUND_ONESOURCE_COUNT_STORY:,} no-transaction-fee funds (story)",
        expanded=True,
    ):
        st.json(mutual_fund_onesource_summary())
        st.dataframe(pd.DataFrame(mock_onesource_fund_sample(10)), use_container_width=True, hide_index=True)

    with st.expander("24/5 extended hours — thinkorswim (2025 story)", expanded=False):
        st.json(extended_hours_trading_story())

    with st.expander("Schwab Crypto™ — Bitcoin & Ethereum (story)", expanded=False):
        st.json(schwab_crypto_account_story())
        st.info("Simulated **availability notice** — you would receive an alert when enrollment opens.")

    with st.expander("Margin trading — rates, buying power, alerts", expanded=False):
        e1, e2 = st.columns(2)
        with e1:
            eq = st.number_input("Account equity ($)", value=100_000.0, step=5000.0)
        with e2:
            deb = st.number_input("Margin debit / loan balance ($)", value=25_000.0, step=1000.0)
        br = st.number_input("Disclosed base rate % (story)", value=MARGIN_BASE_RATE_STORY, step=0.25)
        st.json(margin_account_snapshot(eq, deb, br))

    with st.expander("International stocks — Global Account & ADRs", expanded=False):
        st.json(international_trading_story())

    with st.expander("New issues & IPO participation + Equity Ratings (story)", expanded=False):
        st.json(ipo_and_new_issues_story())
        st.dataframe(pd.DataFrame(mock_ipo_calendar_rows(8)), use_container_width=True, hide_index=True)
