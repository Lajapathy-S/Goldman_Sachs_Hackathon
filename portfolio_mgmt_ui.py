"""
§1.2 Portfolio management UI — simulation; integrates with Streamlit session state.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from portfolio_logic import RiskProfile, allocation_pcts, portfolio_total
from portfolio_mgmt_sim import (
    analyst_mock,
    dividend_events_for_ticker,
    earnings_dates_mock,
    ensure_default_accounts,
    holding_mock_price_ticker,
    news_mock_headlines,
    net_open_unrealized,
    PERF_RANGES,
    sparkline_series,
    synthetic_equity_curve,
    today_change_for_value,
)


def ensure_portfolio_state(ss: Any) -> None:
    if "accounts" not in ss:
        ss.accounts = ensure_default_accounts()
    if "watchlists" not in ss:
        ss.watchlists = {"My first watchlist": ["SPY", "VTI", "AAPL"]}
    if "completed_trades" not in ss:
        ss.completed_trades = []
    if "cash_balance_usd" not in ss:
        ss.cash_balance_usd = 2500.0
    if "gold_card_balance_usd" not in ss:
        ss.gold_card_balance_usd = 0.0
    if "crypto_holdings_usd" not in ss:
        ss.crypto_holdings_usd = 320.0
    if "portfolio_view_account" not in ss:
        ss.portfolio_view_account = "Consolidated"

    for h in ss.holdings:
        h.setdefault("account_id", "acc_main")
        h.setdefault("ticker", "")
        h.setdefault("lots", [])
        if "cost_basis_total" not in h:
            h["cost_basis_total"] = float(h.get("value", 0) or 0) * 0.94
        pr, prev = holding_mock_price_ticker(str(h.get("name", "")), h.get("ticker") or None)
        h.setdefault("mock_price", pr)
        h.setdefault("mock_prev_close", prev)


def filter_holdings(holdings: list[dict], account_filter: str | None) -> list[dict]:
    if not account_filter or account_filter == "Consolidated":
        return holdings
    return [h for h in holdings if h.get("account_id") == account_filter]


def account_total(holdings: list[dict], account_id: str) -> float:
    return sum(float(h.get("value", 0) or 0) for h in holdings if h.get("account_id") == account_id)


def render_unified_portfolio_dashboard(profile: RiskProfile | None) -> None:
    ss = st.session_state
    ensure_portfolio_state(ss)

    st.markdown("### Unified portfolio (simulated)")
    st.caption(
        "§1.2 **Portfolio management** — mock quotes, charts, and tax data for demonstration. "
        "Not live data; not your real broker."
    )

    accounts = ss.accounts
    acc_options = ["Consolidated"] + [a["id"] for a in accounts]
    labels = {"Consolidated": "All accounts"} | {a["id"]: f"{a['name']} ({a['id']})" for a in accounts}
    view = st.selectbox(
        "View",
        acc_options,
        format_func=lambda x: labels.get(x, x),
        key="portfolio_view_account_select",
    )
    ss.portfolio_view_account = view

    hs = filter_holdings(ss.holdings, view if view != "Consolidated" else None)
    total_pv = portfolio_total(hs)
    day_sum = 0.0
    rows = []
    for h in hs:
        v = float(h.get("value", 0) or 0)
        pr = float(h.get("mock_price", 0) or 0)
        pv = float(h.get("mock_prev_close", pr) or pr)
        dd, dp = today_change_for_value(v, pr, pv)
        day_sum += dd
        cost, unreal = net_open_unrealized(h.get("lots") or [], v, float(h.get("cost_basis_total", 0) or 0))
        w = 100.0 * v / total_pv if total_pv > 0 else 0.0
        acc_name = next((a["name"] for a in accounts if a["id"] == h.get("account_id")), "")
        rows.append(
            {
                "Name": h.get("name"),
                "Ticker": h.get("ticker") or "—",
                "Account": acc_name,
                "Value ($)": round(v, 2),
                "Today ($)": round(dd, 2),
                "Today (%)": round(dp, 2),
                "Weight %": round(w, 1),
                "Mock price": round(pr, 2),
                "Cost basis ($)": round(cost, 2),
                "Unrealized ($)": round(unreal, 2),
            }
        )

    pct_day = 100.0 * day_sum / total_pv if total_pv else 0.0

    c1, c2, c3, c4 = st.columns([1.2, 1.2, 1.5, 2])
    with c1:
        st.metric("Portfolio value (mock positions)", f"${total_pv:,.0f}")
    with c2:
        st.metric("Today (simulated)", f"${day_sum:+,.0f}", f"{pct_day:+.2f}%")
    with c3:
        sp_vals, _sp_t = sparkline_series(total_pv if total_pv > 0 else 10000.0, seed=42)
        fig_sp = go.Figure(
            go.Scatter(
                y=sp_vals,
                mode="lines",
                line=dict(color="#27ae60", width=2),
                fill="tozeroy",
                fillcolor="rgba(39,174,96,0.12)",
            )
        )
        fig_sp.update_layout(
            height=120,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
        )
        st.plotly_chart(fig_sp, use_container_width=True, config={"displayModeBar": False})
        st.caption("Performance sparkline (synthetic intraday-style series)")
    with c4:
        if view == "Consolidated":
            st.markdown("**Accounts** — up to 10; consolidated & per-account views.")
        else:
            a = next((x for x in accounts if x["id"] == view), None)
            if a:
                st.markdown(f"**{a['name']}** · {a.get('goal_type', 'Goal')}")
                tgt = a.get("goal_target_usd")
                if tgt and float(tgt) > 0:
                    prog = min(100.0, 100.0 * account_total(ss.holdings, view) / float(tgt))
                    st.progress(prog / 100.0)
                    st.caption(f"Progress toward **${float(tgt):,.0f}** goal: **{prog:.0f}%**")
                if profile and a.get("goal_type"):
                    ap = allocation_pcts(hs)
                    st.caption(
                        f"Suggested mix for your profile: growth **{profile.growth_target_pct:.0f}%**, "
                        f"balanced **{profile.balanced_target_pct:.0f}%**, stable **{profile.stable_target_pct:.0f}%** "
                        "(from Goals tab)."
                    )

    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No holdings in this view — add positions under **My holdings** or load the example.")

    # Performance time-series
    st.markdown("#### Portfolio performance (interactive — mock)")
    range_key = st.radio(
        "Time range",
        PERF_RANGES,
        horizontal=True,
        index=2,
        key="perf_range_radio",
    )

    end_v = total_pv if total_pv > 0 else 10000.0
    idx, vp, vb = synthetic_equity_curve(end_v, range_key, seed=abs(hash(range_key)) % 10_000)
    fig_p = go.Figure()
    fig_p.add_trace(go.Scatter(x=idx, y=vp, name="Portfolio (sim)", line=dict(color="#2980b9")))
    fig_p.add_trace(go.Scatter(x=idx, y=vb, name="S&P 500 (sim benchmark)", line=dict(color="#95a5a6", dash="dot")))
    fig_p.update_layout(
        height=360,
        margin=dict(t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        hovermode="x unified",
        yaxis_title="Value ($)",
    )
    st.plotly_chart(fig_p, use_container_width=True)
    st.caption("Hover for date/value. Benchmark is a **synthetic** correlated series — not an index feed.")

    # Holding detail
    st.markdown("#### Holding detail page (simulated)")
    if hs:
        names = [h.get("name") for h in hs]
        pick = st.selectbox("Choose a holding", names, key="detail_pick")
        h = next(x for x in hs if x.get("name") == pick)
        tk = (h.get("ticker") or "").strip()
        pr = float(h.get("mock_price", 0) or 0)
        t1, t2 = earnings_dates_mock(tk if tk else None)
        acc_theme = next((a.get("theme") for a in accounts if a["id"] == h.get("account_id")), "#2ecc71")
        with st.expander("Price chart (mock)", expanded=True):
            idx2, vp2, _ = synthetic_equity_curve(h.get("value", 1000), "3M", seed=abs(hash(str(pick))) % 9999)
            fig_h = go.Figure(go.Scatter(x=idx2, y=vp2, line=dict(color=acc_theme)))
            fig_h.update_layout(height=260, margin=dict(t=20, b=20), showlegend=False)
            st.plotly_chart(fig_h, use_container_width=True)
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown("**Analyst ratings (mock)**")
            st.json(analyst_mock(tk if tk else None))
        with c_b:
            st.markdown("**Financials (mock)**")
            st.caption("Revenue YoY +8% · Margin flat — placeholder facts.")
        st.markdown("**News (mock)**")
        for line in news_mock_headlines(tk if tk else None):
            st.markdown(f"- {line}")
        st.markdown("**Options chain** — use **Trading (sim)** → Options expander for Greeks-style table.")
        if t1:
            st.caption(f"Next earnings window (mock): **{t1}** (report), **{t2}** (call).")
        divs = dividend_events_for_ticker(tk if tk else None)
        if divs:
            st.markdown("**Upcoming dividends (mock)**")
            st.dataframe(pd.DataFrame(divs), use_container_width=True, hide_index=True)
    else:
        st.caption("Add holdings to open a detail page.")

    # Watchlists
    st.markdown("#### Watchlists (mock prices)")
    wl_names = list(ss.watchlists.keys())
    wl_pick = st.selectbox("List", wl_names, key="wl_pick")
    tickers = ss.watchlists.get(wl_pick, [])
    new_t = st.text_input("Add ticker", key="wl_add").strip().upper()
    if st.button("Add ticker to list"):
        if new_t and new_t not in tickers:
            tickers = tickers + [new_t]
            ss.watchlists[wl_pick] = tickers
            st.rerun()
    wl_rows = []
    for i, t in enumerate(tickers):
        pr, prev = holding_mock_price_ticker(t, t)
        wl_rows.append(
            {
                "#": i + 1,
                "Ticker": t,
                "Mock price": pr,
                "Change %": round((pr / prev - 1) * 100, 2),
            }
        )
    if wl_rows:
        st.dataframe(pd.DataFrame(wl_rows), use_container_width=True, hide_index=True)
    st.caption("Reorder: use **Move up** / **Move down** (drag-drop not available in Streamlit).")
    if tickers and len(tickers) > 1:
        mv = st.selectbox("Move ticker", tickers, key="wl_mv")
        u1, u2 = st.columns(2)
        with u1:
            if st.button("Move up"):
                i = tickers.index(mv)
                if i > 0:
                    tickers[i], tickers[i - 1] = tickers[i - 1], tickers[i]
                    ss.watchlists[wl_pick] = tickers
                    st.rerun()
        with u2:
            if st.button("Move down"):
                i = tickers.index(mv)
                if i < len(tickers) - 1:
                    tickers[i], tickers[i + 1] = tickers[i + 1], tickers[i]
                    ss.watchlists[wl_pick] = tickers
                    st.rerun()
    st.caption("Shareable link: not implemented in prototype — would be a hosted URL with token.")

    # Net worth
    st.markdown("#### Net worth (aggregated — sim)")
    e1, e2, e3 = st.columns(3)
    with e1:
        ss.cash_balance_usd = float(
            st.number_input("Cash ($)", value=float(ss.cash_balance_usd), step=100.0, key="nw_cash")
        )
    with e2:
        ss.crypto_holdings_usd = float(
            st.number_input("Crypto holdings ($)", value=float(ss.crypto_holdings_usd), step=50.0, key="nw_crypto")
        )
    with e3:
        ss.gold_card_balance_usd = float(
            st.number_input("Card / other ($)", value=float(ss.gold_card_balance_usd), step=50.0, key="nw_gold")
        )

    nw = (
        portfolio_total(ss.holdings)
        + float(ss.cash_balance_usd)
        + float(ss.crypto_holdings_usd)
        + float(ss.gold_card_balance_usd)
    )
    n1, n2, n3, n4 = st.columns(4)
    n1.metric("Investments (entered)", f"${portfolio_total(ss.holdings):,.0f}")
    n2.metric("Cash", f"${ss.cash_balance_usd:,.0f}")
    n3.metric("Crypto bucket (sim)", f"${ss.crypto_holdings_usd:,.0f}")
    n4.metric("Card / other (sim)", f"${ss.gold_card_balance_usd:,.0f}")
    st.success(f"**Total net worth (sim components):** ${nw:,.0f}")
    st.caption("Bank integration / Robinhood-style expansion would add linked accounts here.")

    # Tax lots
    st.markdown("#### Tax lot management (simulated)")
    lot_rows = []
    for h in ss.holdings:
        for lot in h.get("lots") or []:
            qty = float(lot.get("qty", 0))
            cps = float(lot.get("cost_per_share", 0))
            acq = lot.get("acq_date", "")
            term = lot.get("term", "LT")
            mv_lot = qty * float(h.get("mock_price", 0) or 0)
            cost_lot = qty * cps
            lot_rows.append(
                {
                    "Position": h.get("name"),
                    "Ticker": h.get("ticker") or "—",
                    "Qty": qty,
                    "Cost/sh": cps,
                    "Acquired": acq,
                    "Term": term,
                    "Unrealized": round(mv_lot - cost_lot, 2),
                }
            )
    if lot_rows:
        st.dataframe(pd.DataFrame(lot_rows), use_container_width=True, hide_index=True)
        st.caption("Sales would allow **specific-lot selection** in a production OMS — here we display only.")
    else:
        st.info("No tax lots — load **example portfolio** (with lots) or add `lots` in session for demo.")

    # Trade history
    st.markdown("#### Per-trade P&L & export (sim)")
    if ss.completed_trades:
        tdf = pd.DataFrame(ss.completed_trades)
        st.dataframe(tdf, use_container_width=True, hide_index=True)
        st.download_button(
            "Download CSV (tax helper)",
            tdf.to_csv(index=False),
            file_name="trade_history_sim.csv",
            mime="text/csv",
        )
    else:
        st.caption("No completed trades logged — example data below when you load demo.")
        st.caption("Realized P&L, holding period, and cost basis export appear here per spec.")

    # Dividend history placeholder
    st.markdown("#### Dividend history (sim)")
    st.caption("Received dividends would appear in **transaction history**; mock upcoming dates show on holding detail.")
    if hs:
        dh = [{"asset": h.get("name"), **ev} for h in hs for ev in dividend_events_for_ticker((h.get("ticker") or "").strip() or None)]
        if dh:
            st.dataframe(pd.DataFrame(dh), use_container_width=True, hide_index=True)

    # Manage accounts
    with st.expander("Manage investing accounts (up to 10)", expanded=False):
        st.markdown("Create named accounts with goal labels — **consolidated** view stays available.")
        if len(accounts) >= 10:
            st.warning("Maximum 10 accounts reached.")
        else:
            with st.form("new_acc"):
                nm = st.text_input("Account name")
                th = st.selectbox("Theme color", ["#3498db", "#e74c3c", "#2ecc71", "#9b59b6", "#f39c12"])
                gt = st.selectbox(
                    "Goal type",
                    ["General investing", "Retirement", "House fund", "Growth", "Emergency"],
                )
                gd = st.date_input("Target date (optional)", value=None)
                gusd = st.number_input("Goal target $ (optional)", min_value=0.0, value=0.0, step=1000.0)
                if st.form_submit_button("Create account"):
                    if nm.strip():
                        aid = f"acc_{uuid.uuid4().hex[:8]}"
                        accounts.append(
                            {
                                "id": aid,
                                "name": nm.strip(),
                                "theme": th,
                                "goal_type": gt,
                                "target_date": gd.isoformat() if gd else None,
                                "goal_target_usd": gusd if gusd > 0 else None,
                            }
                        )
                        ss.accounts = accounts
                        st.success("Account created.")
                        st.rerun()


def patch_demo_for_accounts(ss: st.session_state_proxy) -> None:
    """Enrich demo portfolio for §1.2 showcase."""
    ss.accounts = [
        {
            "id": "acc_main",
            "name": "Growth",
            "theme": "#2ecc71",
            "goal_type": "Growth",
            "target_date": (date.today().replace(year=date.today().year + 10)).isoformat(),
            "goal_target_usd": 50000.0,
        },
        {
            "id": "acc_ret",
            "name": "House fund",
            "theme": "#3498db",
            "goal_type": "House fund",
            "target_date": (date.today().replace(year=date.today().year + 3)).isoformat(),
            "goal_target_usd": 80000.0,
        },
    ]
    ss.holdings = [
        {
            "name": "Total Stock Market ETF",
            "ticker": "VTI",
            "type": "mutual_fund",
            "category": "Equity / growth",
            "value": 12000,
            "account_id": "acc_main",
            "cost_basis_total": 10500,
            "lots": [
                {"qty": 40, "cost_per_share": 220.0, "acq_date": "2024-06-01", "term": "LT"},
                {"qty": 10, "cost_per_share": 245.0, "acq_date": "2025-11-15", "term": "ST"},
            ],
        },
        {
            "name": "Bond Index Fund",
            "ticker": "BND",
            "type": "mutual_fund",
            "category": "Debt / stable",
            "value": 5000,
            "account_id": "acc_ret",
            "cost_basis_total": 5100,
            "lots": [{"qty": 65, "cost_per_share": 78.5, "acq_date": "2023-01-10", "term": "LT"}],
        },
        {
            "name": "Example Co.",
            "ticker": "AAPL",
            "type": "stock",
            "category": "Single stock",
            "value": 3000,
            "account_id": "acc_main",
            "cost_basis_total": 2800,
            "lots": [{"qty": 15, "cost_per_share": 175.0, "acq_date": "2025-09-01", "term": "ST"}],
        },
    ]
    ss.completed_trades = [
        {
            "date": "2025-12-01",
            "ticker": "VTI",
            "side": "SELL",
            "qty": 5,
            "proceeds": 1180.0,
            "cost_basis": 1100.0,
            "realized_pnl": 80.0,
            "term": "LT",
        },
        {
            "date": "2025-11-10",
            "ticker": "AAPL",
            "side": "BUY",
            "qty": 5,
            "proceeds": -920.0,
            "cost_basis": 920.0,
            "realized_pnl": 0.0,
            "term": "—",
        },
    ]
    ss.watchlists = {"Tech": ["AAPL", "MSFT", "GOOGL"], "Broad market": ["VTI", "VOO"]}
