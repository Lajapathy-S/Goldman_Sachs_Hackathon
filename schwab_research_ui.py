"""
Schwab research, learning & market tools — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from schwab_research_sim import (
    EQUITY_RATINGS_UNIVERSE_STORY,
    analyst_ratings_equity_research_story,
    daily_market_commentary_audio_story,
    economic_calendar_rows,
    filter_options_chain,
    fixed_income_bondsource_story,
    market_snapshot_alerts_story,
    mock_alert_presets,
    mock_analyst_consensus,
    mock_bond_screener_rows,
    mock_equity_ratings_sample,
    mock_etf_universe_schwab,
    mock_individual_analyst_ratings,
    mock_option_contracts_screen,
    mock_stock_universe_schwab,
    schwab_equity_ratings_story,
    schwab_learning_center_story,
    schwab_network_live_tv_story,
    screen_etfs_schwab,
    screen_stocks_schwab,
    third_party_research_story,
    unusual_options_activity_story,
)


def render_schwab_research_addons() -> None:
    ss = st.session_state
    ss.setdefault("sr_stk", None)
    ss.setdefault("sr_etf", None)

    st.markdown("### Schwab research & market data *(simulation)*")
    st.caption("Screeners and counts are **illustrative** — not live Schwab or market data.")

    with st.expander(
        f"Schwab Equity Ratings® — {EQUITY_RATINGS_UNIVERSE_STORY:,}+ US stocks (story)", expanded=True
    ):
        st.json(schwab_equity_ratings_story())
        st.dataframe(mock_equity_ratings_sample(), use_container_width=True, hide_index=True)

    with st.expander("Third-Party Research (10+ providers)", expanded=False):
        st.json(third_party_research_story())

    with st.expander("Daily Market Commentary (Audio)", expanded=False):
        st.json(daily_market_commentary_audio_story())

    with st.expander("Schwab Learning Center + Coaching links", expanded=False):
        st.json(schwab_learning_center_story())

    with st.expander("Stock Screener — 100+ criteria (subset demo)", expanded=False):
        if ss.sr_stk is None:
            ss.sr_stk = mock_stock_universe_schwab(28)
        c1, c2, c3 = st.columns(3)
        with c1:
            mpe = st.number_input("Max P/E", value=35.0)
            mindiv = st.number_input("Min dividend yield %", value=0.0)
        with c2:
            ming = st.selectbox("Min Schwab Equity Rating®", ["Any", "B", "A"])
        r = screen_stocks_schwab(
            ss.sr_stk,
            max_pe=mpe,
            min_div_yield=mindiv if mindiv > 0 else None,
            min_rating_letter=None if ming == "Any" else ming,
        )
        st.dataframe(r, use_container_width=True, hide_index=True)
        st.caption("Save / schedule screen runs in production — story only here.")

    with st.expander("ETF Screener — compare up to 5", expanded=False):
        if ss.sr_etf is None:
            ss.sr_etf = mock_etf_universe_schwab(20)
        e1, e2, e3 = st.columns(3)
        with e1:
            mex = st.number_input("Max expense %", value=0.35, format="%.3f")
            my = st.number_input("Min yield %", value=1.0)
        with e2:
            iss = st.selectbox("Issuer", ["All", "Schwab", "iShares", "Vanguard", "SPDR"])
        with e3:
            cat = st.selectbox("Asset class/category", ["All", "US equity", "Intl equity", "Sector", "Bond", "Balanced", "Commodity"])
        er = screen_etfs_schwab(
            ss.sr_etf,
            max_expense=mex,
            min_yield=my,
            issuer=None if iss == "All" else iss,
            category=None if cat == "All" else cat,
        )
        st.dataframe(er, use_container_width=True, hide_index=True)
        pick = st.multiselect("Compare ETFs", er["Ticker"].tolist(), max_selections=5)
        if pick:
            st.dataframe(er[er["Ticker"].isin(pick)], use_container_width=True, hide_index=True)

    with st.expander("Options Screener + unusual activity", expanded=False):
        st.json(unusual_options_activity_story())
        oc = mock_option_contracts_screen()
        v1, v2 = st.columns(2)
        with v1:
            ivf = st.number_input("Min IV %", value=20.0)
        with v2:
            mv = st.number_input("Min volume", value=500.0)
        st.dataframe(filter_options_chain(oc, min_iv_pct=ivf, min_volume=int(mv)), use_container_width=True, hide_index=True)

    with st.expander("Economic Calendar", expanded=False):
        st.dataframe(pd.DataFrame(economic_calendar_rows(10)), use_container_width=True, hide_index=True)

    with st.expander("Fixed Income — BondSource™", expanded=False):
        st.json(fixed_income_bondsource_story())
        st.dataframe(mock_bond_screener_rows(12), use_container_width=True, hide_index=True)

    with st.expander("Analyst Ratings (Equity Research)", expanded=False):
        st.json(analyst_ratings_equity_research_story())
        sym_a = st.text_input("Symbol for consensus (sim)", value="NVDA")
        st.json(mock_analyst_consensus(sym_a))
        st.markdown("**Individual contributors (sim)**")
        st.dataframe(mock_individual_analyst_ratings(sym_a, 6), use_container_width=True, hide_index=True)

    with st.expander("Schwab Network (Live Financial TV)", expanded=False):
        st.json(schwab_network_live_tv_story())

    with st.expander("Schwab Market Snapshot Alerts", expanded=False):
        st.json(market_snapshot_alerts_story())
        st.dataframe(pd.DataFrame(mock_alert_presets()), use_container_width=True, hide_index=True)
