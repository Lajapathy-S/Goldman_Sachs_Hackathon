"""
Mutual fund screener, options idea generator, earnings calendar, credit score — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from financial_addons_sim import (
    LOAD_TYPES,
    MUTUAL_FUNDS_COUNT_STORY,
    credit_score_snapshot,
    earnings_rows_for_symbols,
    mock_mutual_fund_universe,
    options_idea_bundle,
    screen_mutual_funds,
)


def render_financial_addons() -> None:
    ss = st.session_state
    ss.setdefault("fa_mf_universe", None)
    ss.setdefault("earnings_watchlist_csv", "")

    st.markdown("### Funds, options, earnings & credit *(simulation)*")
    st.caption(
        f"Mutual fund universe story: **{MUTUAL_FUNDS_COUNT_STORY:,}+** funds — demo uses a small mock set."
    )

    # Mutual fund screener
    with st.expander("Mutual fund screener — 10,000+ funds (subset demo)", expanded=False):
        if ss.fa_mf_universe is None:
            ss.fa_mf_universe = mock_mutual_fund_universe(48)
        mf = ss.fa_mf_universe
        c1, c2, c3 = st.columns(3)
        with c1:
            min_star = st.slider("Min Morningstar rating (stars)", 1, 5, 3)
        with c2:
            max_exp = st.number_input("Max expense ratio %", value=0.5, step=0.01, format="%.3f")
        with c3:
            load_pref = st.selectbox("Load", ["Any"] + list(LOAD_TYPES))
        c4, c5, c6 = st.columns(3)
        with c4:
            min_ten = st.number_input("Min manager tenure (years)", value=2.0, step=0.5)
        with c5:
            cats = ["All"] + sorted(mf["Category"].unique().tolist())
            cat = st.selectbox("Category", cats)
        with c6:
            max_min_inv = st.number_input("Max minimum investment ($)", value=10000.0, step=500.0)
        zero_only = st.checkbox("Fidelity ZERO funds only", value=False)
        res = screen_mutual_funds(
            mf,
            min_morningstar=min_star,
            max_expense=max_exp,
            load_pref=None if load_pref == "Any" else load_pref,
            min_manager_tenure=min_ten,
            category=cat,
            max_min_investment=max_min_inv,
            zero_only=zero_only,
        )
        if not res.empty and "Fidelity ZERO" in res.columns:

            def _zero_row_highlight(row: pd.Series) -> list[str]:
                if row.get("Fidelity ZERO") == "Yes":
                    return ["background-color: rgba(0,120,90,0.12)"] * len(row)
                return [""] * len(row)

            st.dataframe(
                res.style.apply(_zero_row_highlight, axis=1),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.dataframe(res, use_container_width=True, hide_index=True)
        st.caption("Fidelity ZERO rows are **highlighted** when present (0% expense story).")

    # Options idea generator
    with st.expander("Options idea generator", expanded=False):
        st.markdown(
            "Plain-language **outcomes first**, then example strategies (sim — not a recommendation)."
        )
        oc1, oc2 = st.columns(2)
        with oc1:
            outlook = st.selectbox("Market outlook", ["Bullish", "Neutral", "Bearish"])
        with oc2:
            risk = st.selectbox("Risk tolerance", ["Conservative", "Moderate", "Aggressive"])
        bundle = options_idea_bundle(outlook, risk)
        st.info(bundle["disclaimer"])
        st.markdown(f"**Outlook:** {bundle['outlook_summary']}")
        st.markdown(f"**Your risk setting:** {bundle['risk_posture']}")
        st.markdown("**Possible strategy angles (illustrative)**")
        for s in bundle["strategies"]:
            with st.container():
                st.markdown(f"##### {s['Strategy']}")
                st.write(s["What you might see (plain language)"])
                st.caption(s.get("Sketch", ""))

    # Earnings calendar
    with st.expander("Earnings calendar — holdings & watchlist", expanded=False):
        from_holdings = []
        for h in ss.get("holdings") or []:
            t = (h.get("ticker") or "").strip()
            if t:
                from_holdings.append(t.upper())
        extra = st.text_area(
            "Additional symbols (watchlist, comma or newline separated)",
            value=ss.get("earnings_watchlist_csv") or "",
            height=70,
            placeholder="MSFT, GOOGL",
        )
        ss.earnings_watchlist_csv = extra
        parsed = []
        for part in extra.replace("\n", ",").split(","):
            p = part.strip().upper()
            if p:
                parsed.append(p)
        symbols = list(dict.fromkeys(from_holdings + parsed))
        if not symbols:
            st.warning("Add tickers on **My holdings** or in the box above to see a mock earnings grid.")
        else:
            st.caption(f"Tracking **{len(symbols)}** symbol(s) — dates and EPS are **simulated**.")
            edf = earnings_rows_for_symbols(symbols)
            st.dataframe(edf, use_container_width=True, hide_index=True)
        st.markdown(
            "**Alerts (story):** email / push the evening before and morning of each event — toggle in mobile settings."
        )

    # Credit score
    with st.expander("Credit score integration (Experian / Equifax story)", expanded=False):
        snap = credit_score_snapshot(seed_user=str(ss.get("onboarding") or "demo"))
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Score (sim)", snap["current_score_vantage_like"])
        with c2:
            st.metric("Bureau (story)", snap["bureau_story"])
        st.write("**Monthly history (sim)**")
        st.dataframe(pd.DataFrame(snap["monthly_history_sim"]), use_container_width=True, hide_index=True)
        st.markdown("**Tips to improve**")
        for t in snap["tips"]:
            st.markdown(f"- {t}")
        st.success(snap["note"])
