"""
Robinhood Legend — browser pro workspace (§1.5 simulation in Streamlit).
"""

from __future__ import annotations

from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from cortex_sim import nasdaq_level2_mock
from legend_sim import (
    INDICATOR_CATALOG,
    bollinger,
    generate_ohlcv,
    macd_bundle,
    option_long_call_pnl,
    option_pnl_with_decay,
    rsi_series,
    vwap_series,
)
from trading_sim import mock_futures_contract


def render_legend_tab() -> None:
    ss = st.session_state
    ss.setdefault("legend_layout", "Default · Chart + ladder")
    ss.setdefault("legend_sync_log", ["Workspace loaded (sim)"])
    ss.setdefault("legend_staged_order", None)

    st.subheader("Robinhood Legend — advanced workspace (simulated)")
    st.caption(
        "**Browser-based** pro terminal story — no install. Launched **Oct 2024** framing; "
        "**400+ indicators** in production — we ship a **representative subset** with Plotly."
    )

    # ----- Layout presets -----
    with st.expander("Customizable layout & presets", expanded=False):
        preset = st.radio(
            "Layout preset (persists in session)",
            [
                "Default · Chart + ladder",
                "Charts focus · wide canvas",
                "Research + ladder split",
            ],
            horizontal=True,
            key="legend_layout_radio",
        )
        ss.legend_layout = preset
        st.markdown(
            "**Resize / gadgets:** Streamlit can’t drag panels — this dropdown mimics **saved presets**. "
            "Real Legend persists workspace JSON across devices."
        )

    # ----- Cross-device sync -----
    with st.expander("Cross-device sync (mock)", expanded=False):
        if st.button("Simulate sync from mobile"):
            ts = datetime.now().strftime("%H:%M:%S")
            ss.legend_sync_log.append(f"{ts} — watchlists & alerts merged (sim)")
        for line in ss.legend_sync_log[-6:]:
            st.caption(line)
        st.markdown(
            "**Positions / watchlists / alerts / staged orders** — shown as log lines; "
            "real apps use WebSockets + account service."
        )

    # ----- Advanced charting -----
    st.markdown("#### Advanced charting (subset of 400+ indicators)")
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        sym = st.text_input("Symbol", value="AAPL", key="leg_sym").strip().upper()
    with c_s2:
        seed = st.number_input("Scenario seed", min_value=1, max_value=99999, value=42, key="leg_seed")
    with c_s3:
        chart_style = st.selectbox(
            "Chart style",
            ["Candlestick", "OHLC bars", "Line (close)", "Area (close)"],
            key="leg_chart",
        )

    picks = st.multiselect(
        "Indicators (add to chart)",
        [x[0] for x in INDICATOR_CATALOG],
        default=["SMA (20)", "RSI (14)", "Volume bars"],
        key="leg_inds",
    )

    df = generate_ohlcv(bars=160, seed=int(seed), start_price=160 + (hash(sym) % 80))
    close = df["close"]

    extra_rows = sum(
        [
            "RSI (14)" in picks,
            "MACD" in picks,
            "Volume bars" in picks,
        ]
    )
    n_rows = 1 + extra_rows
    rh = [min(0.55, 1.0 / n_rows)] + [max(0.12, 0.45 / max(extra_rows, 1))] * extra_rows
    s = sum(rh)
    rh = [x / s for x in rh]

    fig = make_subplots(
        rows=n_rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.06,
        row_heights=rh,
    )

    row_price = 1
    cur = 2

    if chart_style == "Candlestick":
        fig.add_trace(
            go.Candlestick(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name=sym,
            ),
            row=row_price,
            col=1,
        )
    elif chart_style == "OHLC bars":
        fig.add_trace(
            go.Ohlc(
                x=df.index,
                open=df["open"],
                high=df["high"],
                low=df["low"],
                close=df["close"],
                name=sym,
            ),
            row=row_price,
            col=1,
        )
    elif chart_style == "Line (close)":
        fig.add_trace(
            go.Scatter(x=df.index, y=df["close"], name="Close", line=dict(width=1)),
            row=row_price,
            col=1,
        )
    else:
        fig.add_trace(
            go.Scatter(x=df.index, y=df["close"], fill="tozeroy", name="Close", line=dict(width=1)),
            row=row_price,
            col=1,
        )

    if "SMA (20)" in picks:
        fig.add_trace(
            go.Scatter(x=df.index, y=close.rolling(20).mean(), name="SMA20", line=dict(width=1)),
            row=row_price,
            col=1,
        )
    if "EMA (12)" in picks:
        fig.add_trace(
            go.Scatter(x=df.index, y=close.ewm(span=12, adjust=False).mean(), name="EMA12", line=dict(width=1)),
            row=row_price,
            col=1,
        )
    if "Bollinger Bands" in picks:
        u, _m, l = bollinger(close, 20)
        fig.add_trace(go.Scatter(x=df.index, y=u, name="BB upper", line=dict(width=1, dash="dot")), row=row_price, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=l, name="BB lower", line=dict(width=1, dash="dot")), row=row_price, col=1)
    if "VWAP" in picks:
        fig.add_trace(
            go.Scatter(x=df.index, y=vwap_series(df), name="VWAP", line=dict(width=1, color="purple")),
            row=row_price,
            col=1,
        )

    if "RSI (14)" in picks:
        rsi = rsi_series(close)
        fig.add_trace(go.Scatter(x=df.index, y=rsi, name="RSI"), row=cur, col=1)
        fig.add_hline(y=70, line_dash="dash", row=cur, col=1)
        fig.add_hline(y=30, line_dash="dash", row=cur, col=1)
        fig.update_yaxes(range=[0, 100], row=cur, col=1)
        cur += 1

    if "MACD" in picks:
        ml, sig, hist = macd_bundle(close)
        fig.add_trace(go.Scatter(x=df.index, y=ml, name="MACD"), row=cur, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=sig, name="Signal"), row=cur, col=1)
        fig.add_trace(go.Bar(x=df.index, y=hist, name="Hist"), row=cur, col=1)
        cur += 1

    if "Volume bars" in picks:
        fig.add_trace(
            go.Bar(x=df.index, y=df["volume"], name="Volume", marker_color="rgba(80,80,120,0.45)"),
            row=cur,
            col=1,
        )

    fig.update_layout(
        height=min(200 + n_rows * 160, 780),
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=40, b=20),
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "**Drawing tools** (trend lines, Fibonacci): not interactive here — Legend desktop draws on canvas; "
        "we focus on **indicator math visibility** for your demo."
    )

    # ----- Order ladder -----
    st.markdown("#### Order ladder — depth & click-to-stage (sim)")
    lad_sym = st.text_input("Ladder symbol", value=sym, key="lad_sym").strip().upper()
    bids, asks = nasdaq_level2_mock(lad_sym, levels=12)
    bc1, bc2 = st.columns(2)
    with bc1:
        st.markdown("**Asks** (sell side)")
        st.dataframe(asks.iloc[::-1], use_container_width=True, hide_index=True)
    with bc2:
        st.markdown("**Bids**")
        st.dataframe(bids, use_container_width=True, hide_index=True)
    pick_side = st.radio("Stage order", ["Bid", "Ask"], horizontal=True, key="lad_side")
    prices = bids["price"].tolist() if pick_side == "Bid" else asks["price"].tolist()
    px_pick = st.selectbox("Click price level (sim)", [f"{p:.2f}" for p in prices])
    if st.button("Stage limit order at selected level"):
        ss.legend_staged_order = {"symbol": lad_sym, "side": pick_side, "price": float(px_pick)}
        st.success(f"Staged **{pick_side}** @ **${px_pick}** — would sync to mobile (sim).")

    # ----- Simulated returns (options) -----
    st.markdown("#### Simulated returns — option P&L (pre-trade)")
    o1, o2, o3, o4 = st.columns(4)
    with o1:
        strike = st.number_input(
            "Strike",
            min_value=1.0,
            value=float(round(float(close.iloc[-1]), 2)),
            step=1.0,
        )
    with o2:
        premium = st.number_input("Premium / share", min_value=0.01, value=4.5, step=0.1)
    with o3:
        contracts = st.number_input("Contracts", min_value=1, value=1, step=1)
    with o4:
        theta_f = st.slider("Time decay (story)", 0.0, 0.4, 0.15)

    lo = strike * 0.85
    hi = strike * 1.15
    grid = np.linspace(lo, hi, 80)
    pnl_exp = option_long_call_pnl(grid, strike, premium, int(contracts))
    pnl_theta = option_pnl_with_decay(grid, strike, premium, theta_f, 0.0, int(contracts))

    figp = go.Figure()
    figp.add_trace(go.Scatter(x=grid, y=pnl_exp, name="Expiry-style payoff"))
    figp.add_trace(go.Scatter(x=grid, y=pnl_theta, name="With θ-style shrink (toy)"))
    figp.update_layout(
        title="P&L vs underlying (illustrative)",
        xaxis_title="Underlying price",
        yaxis_title="P&L ($)",
        height=380,
    )
    st.plotly_chart(figp, use_container_width=True)
    st.caption(
        "**Theta / IV:** decay slider scales risk toy curve; production tool charts **multi-expiry** surfaces."
    )

    # ----- Futures -----
    st.markdown("#### Futures on Legend (sim)")
    fut_pick = st.selectbox("Contract", ["ES (S&P)", "NQ (Nasdaq)", "CL (Oil)"], key="leg_fut")
    fc = fut_pick.split()[0]
    st.json(mock_futures_contract(fc.replace("(", "").replace(")", "")))
    st.caption("**Q4 2025** rollout story — margin & sizing mirror **Trading (sim)** futures expander.")

    # ----- Cortex on Legend -----
    with st.expander("Cortex AI on Legend (Gold — early 2026 story)", expanded=False):
        st.markdown(
            "**Digests**, **NL screeners**, and **custom indicators** attach to chart context in Legend; "
            "use the **Research & AI (sim)** tab for the same flows here."
        )
        if st.button("Open Cortex mindset"):
            st.info("Navigate to **Research & AI (sim)** — integrated sidebar modules mirror Legend UX.")
