"""
§2.5 Research, education & market data — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from research_education_sim import (
    EXPERIENCE_LEVELS,
    HELP_SNIPPETS,
    LEARNING_RESOURCES_COUNT_STORY,
    THIRD_PARTY_PROVIDERS,
    TOPICS,
    aggregated_analyst_score,
    learning_resources_catalog,
    mock_etf_universe,
    mock_stock_universe,
    screen_etfs,
    screen_stocks,
    viewpoints_weekly_issues,
)


def render_research_education_addons() -> None:
    ss = st.session_state
    ss.setdefault("re_saved_screeners", [])
    ss.setdefault("re_stk_universe", None)
    ss.setdefault("re_etf_universe", None)

    st.markdown("### Research, education & market data *(§2.5 simulation)*")
    st.caption("Library counts and screeners are **illustrative** — not live Fidelity or market data.")

    # Learning Center
    with st.expander(f"Fidelity Learning Center — **{LEARNING_RESOURCES_COUNT_STORY}+** resources (sim)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            exp_f = st.selectbox("Experience level", ["All"] + list(EXPERIENCE_LEVELS))
        with c2:
            top_f = st.selectbox("Topic", ["All topics"] + list(TOPICS))
        exp_arg = None if exp_f == "All" else exp_f
        top_arg = None if top_f == "All topics" else top_f
        cat = learning_resources_catalog(
            experience=exp_arg,
            topic=top_arg,
            n=12,
            seed=hash(f"{exp_f}{top_f}") % 10000,
        )
        st.dataframe(cat, use_container_width=True, hide_index=True)

    # Contextual help
    with st.expander("Contextual in-product help — “What is this?”", expanded=False):
        st.markdown("Plain-language definitions without leaving the page (sim).")
        for term, text in HELP_SNIPPETS.items():
            with st.expander(f"What is **{term}**?"):
                st.write(text)

    # Viewpoints
    with st.expander("Fidelity Viewpoints — weekly market analysis (sim)", expanded=False):
        for v in viewpoints_weekly_issues(5):
            st.markdown(f"- **{v['Headline']}** — {v['Format']} · {v['Week']}")
        st.caption("Strategist outlook, sector, economy, options education — video + article mix in production.")

    # Third-party research
    with st.expander("Third-party research aggregation", expanded=False):
        st.write("Providers (story): **" + "**, **".join(THIRD_PARTY_PROVIDERS) + "**")
        sym = st.text_input("Symbol for blended score", value="AAPL").strip().upper()
        st.json(aggregated_analyst_score(sym))
        st.caption("One consolidated score with links to underlying reports in a full platform.")

    # Bloomberg TV
    with st.expander("Bloomberg TV (mobile app integration)", expanded=False):
        st.info(
            "**Live stream** of Bloomberg TV in the **mobile** news tab during market hours (story) — "
            "no video player in this Streamlit build."
        )

    # Stock screener
    with st.expander("Stock screener — 140+ criteria (subset demo)", expanded=False):
        if ss.re_stk_universe is None:
            ss.re_stk_universe = mock_stock_universe(30)
        df0 = ss.re_stk_universe
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            max_pe = st.number_input("Max P/E", value=30.0, step=1.0)
        with c2:
            min_eps = st.number_input("Min EPS growth %", value=-5.0, step=1.0)
        with c3:
            max_rsi = st.number_input("Max RSI (14)", value=70.0, step=1.0)
        with c4:
            sec = st.selectbox("Sector", ["All", "Tech", "Healthcare", "Financials", "Industrial", "Consumer", "Energy"])
        res = screen_stocks(
            df0, max_pe=max_pe, min_eps_growth=min_eps, max_rsi=max_rsi, sector=None if sec == "All" else sec
        )
        st.dataframe(res, use_container_width=True, hide_index=True)
        name = st.text_input("Save screener as", value="My value list")
        if st.button("Save screener (session)"):
            ss.re_saved_screeners.append(
                {"name": name, "type": "stock", "count": len(res), "filters": f"P/E<={max_pe}, EPS>={min_eps}"}
            )
        st.caption("Schedule screener runs in production — here we only store a label.")
        if ss.re_saved_screeners:
            st.dataframe(pd.DataFrame(ss.re_saved_screeners), use_container_width=True, hide_index=True)

    # ETF screener
    with st.expander("ETF screener & compare (up to 5)", expanded=False):
        if ss.re_etf_universe is None:
            ss.re_etf_universe = mock_etf_universe(20)
        edf0 = ss.re_etf_universe
        e1, e2, e3 = st.columns(3)
        with e1:
            max_ex = st.number_input("Max expense %", value=0.3, step=0.01, format="%.3f", key="etf_ex")
        with e2:
            min_y = st.number_input("Min yield %", value=0.0, step=0.1, key="etf_yld")
        with e3:
            ac = st.selectbox("Asset class", ["All", "US equity", "Intl equity", "Fixed income", "Balanced"], key="etf_ac")
        fam = st.selectbox("Fund family", ["All", "Fidelity", "Vanguard", "iShares", "SPDR"], key="etf_fam")
        eres = screen_etfs(
            edf0,
            max_expense=max_ex,
            min_yield=min_y,
            asset_class=None if ac == "All" else ac,
            family=None if fam == "All" else fam,
        )
        st.dataframe(eres, use_container_width=True, hide_index=True)
        pick = st.multiselect("Compare up to 5 ETFs", eres["Ticker"].tolist(), max_selections=5)
        if pick:
            st.dataframe(eres[eres["Ticker"].isin(pick)], use_container_width=True, hide_index=True)
