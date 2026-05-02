"""
Fidelity Trader+ add-ons (Add-ons tab) — simulation only.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from trader_plus_sim import (
    CHART_STYLES,
    CHART_TIMEFRAMES,
    CRYPTO_TRADER_PLUS,
    INDICATOR_COUNT_STORY,
    LAUNCH_STORY,
    heikin_ashi,
    long_call_analytics,
    mock_streaming_quote,
    ohlc_for_timeframe,
    paper_backtest_equity_curve,
    rough_itm_probability,
)


def render_trader_plus_addons() -> None:
    ss = st.session_state
    ss.setdefault("tp_sync_log", ["Trader+ workspace (sim) initialized"])
    ss.setdefault("tp_saved_orders", [])
    ss.setdefault("tp_paper_cash", 100_000.0)
    ss.setdefault("tp_paper_positions", [])
    ss.setdefault("tp_trade_context", None)

    st.markdown("### Fidelity Trader+ *(simulation)*")
    st.success(LAUNCH_STORY)
    st.caption(
        "**Free** to self-directed customers · **desktop app**, **web**, **mobile** · cross-device sync story — "
        "no real Fidelity connectivity."
    )

    # Ecosystem & sync
    with st.expander("Trader+ ecosystem · cross-device continuation", expanded=True):
        if st.button("Simulate: started analysis on desktop → complete on mobile"):
            ss.tp_trade_context = {
                "stage": "Order ticket staged",
                "symbol": "SPY",
                "from": "desktop (sim)",
            }
            ss.tp_sync_log.append("Context handed off mobile ↔ desktop (sim)")
        if ss.tp_trade_context:
            st.json(ss.tp_trade_context)
        if st.button("Simulate instant sync pulse"):
            ss.tp_sync_log.append("Watchlists / positions / saved orders synced (sim)")
        for line in ss.tp_sync_log[-5:]:
            st.caption(line)

    # Advanced charting
    with st.expander(f"Advanced charting — **{INDICATOR_COUNT_STORY}+** indicators (subset demo)", expanded=False):
        st.markdown(
            "**Types:** candlestick, bar, line, **Heikin-Ashi** · **Drawing tools** (Fib, trend, pitchfork) = canvas feature in full app."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            tf = st.selectbox("Timeframe", CHART_TIMEFRAMES, index=4)
        with c2:
            style = st.selectbox("Chart style", CHART_STYLES)
        with c3:
            seed = st.number_input("Series seed", min_value=1, max_value=99999, value=7)

        df = ohlc_for_timeframe(tf, bars=120, seed=int(seed))
        if style.startswith("Heikin"):
            df_plot = heikin_ashi(df)
        else:
            df_plot = df

        fig = go.Figure()
        if style == "Candlestick" or style.startswith("Heikin"):
            fig.add_trace(
                go.Candlestick(
                    x=df_plot.index,
                    open=df_plot["open"],
                    high=df_plot["high"],
                    low=df_plot["low"],
                    close=df_plot["close"],
                    name="Price",
                )
            )
        elif "Bar" in style:
            fig.add_trace(
                go.Ohlc(
                    x=df_plot.index,
                    open=df_plot["open"],
                    high=df_plot["high"],
                    low=df_plot["low"],
                    close=df_plot["close"],
                    name="OHLC",
                )
            )
        else:
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot["close"], name="Close"))

        fig.update_layout(height=420, template="plotly_white", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

    # Streaming quotes
    with st.expander("Streaming Level 1 quotes (mock)", expanded=False):
        sq_sym = st.text_input("Symbol", value="QQQ", key="tp_quote_sym").strip().upper()
        if st.button("Refresh stream tick", key="tp_stream_btn"):
            q = mock_streaming_quote(sq_sym)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Last", f"${q['last']}")
            m2.metric("Bid / Ask", f"${q['bid']} / ${q['ask']}")
            m3.metric("Sizes", f"{q['size_bid']} / {q['size_ask']}")
            m4.metric("Clock", q["ts"])
            st.caption(q["data_level"])
        else:
            st.caption("Tap **Refresh stream tick** for a live-style L1 snapshot (no websocket).")

    # Saved & conditional orders
    with st.expander("Saved orders & conditional (OTO / OCO)", expanded=False):
        with st.form("tp_save_order"):
            nm = st.text_input("Template name", value="Opening bounce")
            typ = st.selectbox("Order story", ["OTO — one triggers other", "OCO — one cancels other", "Bracket (sim)"])
            notes = st.text_area("Notes", value="Limit entry + take-profit child")
            if st.form_submit_button("Save template"):
                ss.tp_saved_orders.append({"name": nm, "type": typ, "notes": notes})
                st.success("Saved for reuse across sessions **in this browser**.")
        if ss.tp_saved_orders:
            st.dataframe(pd.DataFrame(ss.tp_saved_orders), use_container_width=True, hide_index=True)

    # Options analytics
    with st.expander("Options analytics suite", expanded=False):
        k = st.number_input("Strike", min_value=1.0, value=450.0)
        pr = st.number_input("Premium / share", min_value=0.01, value=6.0)
        n = st.number_input("Contracts", min_value=1, value=2)
        spot = st.number_input("Spot (for prob)", min_value=1.0, value=448.0)
        days = st.number_input("Days to expiry", min_value=1.0, value=30.0)
        iv = st.slider("IV (annual)", 0.05, 1.0, 0.25)
        an = long_call_analytics(k, pr, int(n))
        st.json(an)
        st.metric("Rough ITM probability (toy)", f"{rough_itm_probability(spot, k, days, iv) * 100:.1f}%")
        grid = np.linspace(max(1.0, k * 0.85), k * 1.15, 60)
        intrinsic = np.maximum(grid - k, 0) - pr
        pnl = intrinsic * 100 * int(n)
        figp = go.Figure(go.Scatter(x=grid, y=pnl, name="P&L @ expiry style"))
        figp.add_vline(x=an["breakeven"], line_dash="dash", annotation_text="Breakeven")
        figp.update_layout(title="Long call P&L (illustrative)", height=360)
        st.plotly_chart(figp, use_container_width=True)

    # Mobile
    with st.expander("Mobile Trader+ (story)", expanded=False):
        st.markdown(
            "**Rebuilt** mobile UX · charts · streaming · chain · order entry · **Face ID / Touch ID** login framing."
        )

    # Screen sharing
    with st.expander("Screen sharing with specialists", expanded=False):
        st.info(
            "**Desktop** embeds screen share with trading specialists; **24/7** phone/chat/social support story for active traders — no video session in prototype."
        )

    # Crypto
    with st.expander("Fidelity Crypto on Trader+", expanded=False):
        st.caption("BTC, ETH, select altcoins — **web/mobile**; desktop integration **2026** story.")
        pick = st.multiselect("Symbols", CRYPTO_TRADER_PLUS, default=["BTC", "ETH"])
        rows = [{"symbol": p, "mock_last": round(100 + hash(p) % 5000 + len(p), 2)} for p in pick]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # Paper / ATR simulation
    with st.expander("Paper trading / Active Trader Research simulation", expanded=False):
        st.markdown("Test strategies **without** risking capital · **historical backtest** curve (mock).")
        if st.button("Run mock backtest equity curve"):
            s = paper_backtest_equity_curve()
            figb = go.Figure(go.Scatter(x=s.index, y=s.values, name="Equity"))
            figb.update_layout(height=300, title="Simulated equity path")
            st.plotly_chart(figb, use_container_width=True)
        st.metric("Paper cash balance (sim)", f"${ss.tp_paper_cash:,.0f}")
        st.caption("Extend with paper order buttons if you want a full paper blotter later.")
