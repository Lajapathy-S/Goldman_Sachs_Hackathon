"""
Research & AI (Cortex-style) — simulation UI for classroom prototype.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from cortex_sim import (
    cortex_market_digest,
    custom_indicator_thinkscript,
    earnings_calendar_rows,
    morningstar_premium_mock,
    nasdaq_level2_mock,
    nl_screener_plan,
    personalized_news_lines,
    post_earnings_reaction,
    run_screen,
)
from portfolio_mgmt_sim import analyst_mock


def _tickers_from_session(ss: Any) -> list[str]:
    ensure = ss.holdings if hasattr(ss, "holdings") else []
    t = []
    for h in ensure:
        tk = (h.get("ticker") or "").strip()
        if tk:
            t.append(tk.upper())
    wl = getattr(ss, "watchlists", {}) or {}
    for _name, syms in wl.items():
        for s in syms:
            if s:
                t.append(str(s).upper())
    seen = set()
    out = []
    for x in t:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def render_cortex_research_tab() -> None:
    ss = st.session_state
    ss.setdefault("cortex_gold", True)
    ss.setdefault("price_alerts", [])

    st.subheader("Research & AI (simulated)")
    st.caption(
        "Maps **Cortex**, **Gold**, Morningstar-style research, Level 2, and alerts — "
        "**mock content only**; no large language model calls in this prototype."
    )

    st.toggle(
        "Simulate **Gold subscriber** (unlocks screener, Morningstar mock, Level 2)",
        key="cortex_gold",
    )
    gold = bool(ss.cortex_gold)

    # ----- Cortex digest -----
    with st.expander("**Cortex — AI market digest** (3 sentences)", expanded=True):
        sym_d = st.text_input("Symbol", value="NVDA", key="cortex_sym").strip().upper()
        if st.button("Generate digest", key="btn_digest"):
            sentences, footer = cortex_market_digest(sym_d or "SPY")
            for s in sentences:
                st.markdown(f"· {s}")
            st.caption(footer)

    # ----- NL screener -----
    with st.expander("**Cortex custom scans** (natural language → filters)", expanded=False):
        if not gold:
            st.warning("Spec: **Gold subscribers** — toggle Gold above to preview.")
        q = st.text_area(
            "Describe your screen",
            value="Show me tech stocks with strong earnings momentum and low debt",
            height=70,
            key="nl_screen_q",
        )
        if st.button("Run AI planner (rule-based sim)", key="btn_screen") and gold:
            plan, filt = nl_screener_plan(q)
            st.markdown(plan)
            st.dataframe(run_screen(filt), use_container_width=True, hide_index=True)
            st.caption("Returns are **mock universe rows**, not live listings.")

    # ----- Custom indicators -----
    with st.expander("**Cortex custom indicators** (thinkscript-style stub)", expanded=False):
        if not gold:
            st.warning("Spec: **Gold / Q1 2026** launch framing — enable Gold to preview.")
        ind_prompt = st.text_input(
            "Prompt the chart assistant",
            value="Show RSI with alerts when oversold",
            key="ind_prompt",
        )
        if st.button("Generate indicator logic", key="btn_ind") and gold:
            code, explain = custom_indicator_thinkscript(ind_prompt)
            st.code(code, language="text")
            st.info(explain)

    # ----- Morningstar -----
    with st.expander("**Morningstar Premium** research (mock)", expanded=False):
        if not gold:
            st.warning("Spec: **Gold** unlimited reports (~1,700 names in production).")
        ms_sym = st.text_input("Symbol", value="AAPL", key="ms_sym").strip().upper()
        if st.button("Load analyst report summary", key="btn_ms") and gold:
            rep = morningstar_premium_mock(ms_sym)
            st.metric("Analyst rating", rep["analyst_rating"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Fair value (mock)", f"${rep['fair_value_estimate']}")
            c2.metric("Uncertainty", rep["uncertainty_rating"])
            c3.metric("Economic moat", rep["economic_moat"])
            st.markdown(rep["report_blurb"])

    # ----- Level 2 -----
    with st.expander("**Level 2** Nasdaq book depth (mock)", expanded=False):
        if not gold:
            st.warning("Spec: **Gold** real-time depth — simulation below.")
        l2_sym = st.text_input("Symbol", value="SPY", key="l2_sym").strip().upper()
        if st.button("Show order book", key="btn_l2"):
            bids, asks = nasdaq_level2_mock(l2_sym)
            b1, b2 = st.columns(2)
            with b1:
                st.markdown("**Bids**")
                st.dataframe(bids, use_container_width=True, hide_index=True)
            with b2:
                st.markdown("**Asks**")
                st.dataframe(asks, use_container_width=True, hide_index=True)
            st.caption("Sizes are **randomized placeholders** — not exchange feed.")

    # ----- Analyst summary -----
    with st.expander("**Analyst ratings summary** (free tier style)", expanded=False):
        ar_sym = st.text_input("Symbol", value="MSFT", key="ar_sym").strip().upper()
        if st.button("Show consensus", key="btn_ar"):
            st.json(analyst_mock(ar_sym))

    # ----- Earnings calendar -----
    with st.expander("**Earnings calendar** + post-earnings reaction (mock)", expanded=False):
        tickers = _tickers_from_session(ss)
        manual = st.text_input(
            "Extra tickers (comma-separated)",
            value=",".join(tickers[:5]) if tickers else "AAPL,MSFT",
            key="earn_tick",
        )
        merged = [x.strip().upper() for x in manual.split(",") if x.strip()]
        if st.button("Refresh calendar", key="btn_cal"):
            df_e = earnings_calendar_rows(merged)
            if not df_e.empty:
                st.dataframe(df_e, use_container_width=True, hide_index=True)
            react_sym = merged[0] if merged else "AAPL"
            st.markdown("**Post-earnings reaction (illustrative)**")
            st.json(post_earnings_reaction(react_sym))

    # ----- News -----
    with st.expander("**Personalized news feed** (holdings + watchlists)", expanded=False):
        if st.button("Refresh headlines", key="btn_news"):
            lines = personalized_news_lines(_tickers_from_session(ss))
            st.dataframe(pd.DataFrame(lines), use_container_width=True, hide_index=True)
            st.caption("Sources labeled mock — real apps ingest wires & licenses.")

    # ----- Price alerts -----
    with st.expander("**Price alerts**", expanded=False):
        a1, a2, a3 = st.columns(3)
        with a1:
            al_sym = st.text_input("Symbol", key="al_sym").strip().upper()
        with a2:
            al_dir = st.selectbox("When price", ["above", "below"], key="al_dir")
        with a3:
            al_px = st.number_input("Target ($)", min_value=0.0, value=100.0, step=1.0, key="al_px")
        if st.button("Save alert (in-session)"):
            if al_sym:
                ss.price_alerts.append(
                    {"symbol": al_sym, "direction": al_dir, "target": al_px, "channel": "push + in-app (sim)"}
                )
                st.success("Alert stored for this session.")
        if ss.price_alerts:
            st.dataframe(pd.DataFrame(ss.price_alerts), use_container_width=True, hide_index=True)
