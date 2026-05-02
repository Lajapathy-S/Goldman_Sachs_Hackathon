"""
Streamlit UI: simulated trading desk (maps to a broker-style spec — demo only).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from trading_sim import (
    MOCK_CRYPTO,
    MOCK_STOCK_ETF,
    OPTION_CHAIN_ROWS,
    ORDER_TYPE_HELP,
    fractional_shares,
    instant_deposit_limits,
    mock_futures_contract,
    mock_short_info,
    next_recurring_date,
)


def render_trading_sim_tab(portfolio_total_usd: float) -> None:
    st.subheader("Trading desk (simulation)")
    st.error(
        "**Simulation only.** Nothing here connects to a brokerage or blockchain. "
        "Prices, Greeks, and margins are **made-up teaching numbers**."
    )

    # ----- In-app order ticket + stocks/ETFs -----
    with st.expander("Commission-free stocks & ETFs · Order ticket (sim)", expanded=True):
        st.caption(
            "Spec: **$0 commission** US-listed stocks & ETFs; market / limit / stop / trailing "
            "supported — here you preview labels and estimated cost **without** placing real trades."
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            sym = st.selectbox(
                "Symbol (mock list)",
                list(MOCK_STOCK_ETF.keys()),
                help="Live apps fetch real symbols — we use a tiny static list.",
            )
        with c2:
            side = st.radio("Side", ["Buy", "Sell"], horizontal=True)
        with c3:
            ord_type = st.selectbox("Order type", list(ORDER_TYPE_HELP.keys()))
        st.caption(ORDER_TYPE_HELP[ord_type])

        ref_price = MOCK_STOCK_ETF[sym]
        st.metric("Mock last price (not live)", f"${ref_price:,.2f}")

        mode = st.radio("Size by", ["Dollar amount", "Whole + fractional shares"], horizontal=True)
        if mode == "Dollar amount":
            dollars = st.number_input("Invest ($)", min_value=1.0, value=100.0, step=1.0)
            qty, qty_msg = fractional_shares(dollars, ref_price)
            st.success(f"**Fractional math:** {qty_msg} ≈ **${dollars:,.2f}** ÷ **${ref_price:,.2f}**")
        else:
            qty = st.number_input("Shares", min_value=0.000001, value=1.5, format="%.6f")
            dollars = qty * ref_price
            st.info(f"Notional ≈ **${dollars:,.2f}** at mock ${ref_price:,.2f}")

        limit_px = st.number_input(
            "Limit / stop reference ($, if applicable)",
            min_value=0.0,
            value=float(ref_price),
            step=0.01,
            help="Trailing / stops would use more fields in production.",
        )

        est_commission = 0.0
        st.markdown(
            f"**Estimated commission:** ${est_commission:.2f} (spec: commission-free equities). "
            f"**Minimum balance for this demo:** none — notional **${dollars:,.2f}**."
        )

        if st.button("Review practice ticket (does not trade)", type="primary"):
            st.session_state.setdefault("practice_orders", []).append(
                {
                    "symbol": sym,
                    "side": side,
                    "type": ord_type,
                    "qty": qty,
                    "ref": ref_price,
                    "limit_hint": limit_px,
                }
            )
            st.success("Logged to **Practice log** below.")

        st.markdown("##### Bid / ask (mock)")
        spread = 0.02
        st.code(
            f"Bid ${ref_price - spread/2:.2f}  |  Ask ${ref_price + spread/2:.2f}  (illustrative spread)",
            language=None,
        )

    # ----- Fractional detail -----
    with st.expander("Fractional share investing", expanded=False):
        st.markdown(
            "Spec: invest from **$1**; platform computes share fraction from dollars. "
            "Above, dollar mode shows **six decimal** share quantity — typical apps round for display."
        )

    # ----- Recurring -----
    with st.expander("Recurring investments (schedule preview)", expanded=False):
        st.caption(
            "Spec: daily / weekly / bi-weekly / monthly; executes market-style on chosen cadence "
            "(prototype shows **next calendar date** only)."
        )
        rc_sym = st.selectbox("Symbol", list(MOCK_STOCK_ETF.keys()), key="rc_sym")
        rc_freq = st.selectbox(
            "Frequency",
            ["Daily", "Weekly", "Bi-weekly", "Monthly"],
        )
        rc_amt = st.number_input("Amount per run ($)", min_value=1.0, value=25.0, key="rc_amt")
        nd = next_recurring_date(rc_freq)
        st.info(
            f"Next illustrative run: **{nd.isoformat()}** — **${rc_amt:,.2f}** into **{rc_sym}** "
            f"(fractional shares at that day’s price in a real system)."
        )

    # ----- Extended hours -----
    with st.expander("24/5 extended & overnight sessions (education)", expanded=False):
        st.markdown(
            "**Pre-market / after-hours / overnight:** live brokers restrict order types (often **limit**). "
            "Here: tick **Extended-hours limit style** on your practice ticket intent."
        )
        st.checkbox(
            "I intend this as an extended-hours limit-style instruction (simulated checkbox)",
            value=False,
            key="ext_hours",
        )
        st.caption("900+ symbols — not modeled; regulatory disclosures would appear pre-trade in production.")

    # ----- Options -----
    with st.expander("Options — chain preview (mock Greeks)", expanded=False):
        st.caption(
            "Spec: calls/puts, spreads, chain with IV / OI / volume / bid-ask — **mock chain** for SPY-style strikes."
        )
        strat = st.selectbox(
            "Strategy label",
            [
                "Long call",
                "Long put",
                "Covered call",
                "Cash-secured put",
                "Debit spread",
                "Credit spread",
            ],
        )
        df = pd.DataFrame(OPTION_CHAIN_ROWS)
        df.rename(
            columns={
                "iv": "IV",
                "delta_c": "Delta (call)",
                "gamma": "Gamma",
                "theta": "Theta",
                "vega": "Vega",
                "oi": "Open interest",
                "vol": "Volume",
            },
            inplace=True,
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption(f"Selected strategy label: **{strat}** — simulated returns tool would run pre-trade in a full app.")

    # ----- Index options -----
    with st.expander("Index options (SPX / NDX / RUT style)", expanded=False):
        st.markdown(
            "Spec: cash-settled index options, extended session availability, **per-contract fee** in live brokers."
        )
        n_contracts = st.number_input("Contracts (illustrative)", min_value=1, value=1)
        fee_pc = st.number_input("Assumed per-contract fee ($)", min_value=0.0, value=0.65, step=0.05)
        st.metric("Illustrative contract fees", f"${n_contracts * fee_pc:,.2f}")

    # ----- Futures -----
    with st.expander("Futures (desktop / margin — mock)", expanded=False):
        fut = st.selectbox("Contract family", ["ES (S&P)", "NQ (Nasdaq)", "RTY (Russell)", "CL (Oil)"])
        code = fut.split()[0]
        info = mock_futures_contract(code.replace("(", "").replace(")", ""))
        st.json(info)
        st.warning("Spec: **margin required**; rollout channels vary — this UI is a placeholder only.")

    # ----- Short selling -----
    with st.expander("Short selling — borrow / SI / days-to-cover (mock)", expanded=False):
        ss_sym = st.text_input("Symbol", value="TSLA")
        si = mock_short_info(ss_sym.upper())
        st.metric("Borrow rate (illustrative APR)", f"{si.borrow_rate_apy:.2f}%")
        st.metric("Short interest (% of float, fake)", f"{si.short_interest_pct:.2f}%")
        st.metric("Days to cover (fake)", f"{si.days_to_cover:.2f}")
        st.error(
            "Risk disclosure (required pre-trade): short losses can exceed your initial position; "
            "margin calls may force buy-ins."
        )

    # ----- Crypto -----
    with st.expander("Crypto — many assets · tick refresh (mock)", expanded=False):
        pick = st.multiselect(
            "Assets (subset)",
            list(MOCK_CRYPTO.keys()),
            default=["BTC", "ETH"],
        )
        now_s = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        rows = [{"symbol": p, "mock_price": MOCK_CRYPTO[p], "last_refresh": now_s} for p in pick]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Spec: limit/market; **not** executed here. Prices frozen mock values.")

    # ----- Staking -----
    with st.expander("ETH & SOL staking (APY display mock)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.metric("ETH staking APY (example)", "3.2%")
        with c2:
            st.metric("SOL staking APY (example)", "6.1%")
        st.caption("Rewards can change; lock-up rules vary by network — read issuer disclosures in real apps.")

    # ----- Wallet -----
    with st.expander("Self-custody wallet (concept)", expanded=False):
        st.markdown(
            "**Non-custodial** wallets mean **you** hold keys — transfers to/from brokerage are separate flows. "
            "Chains mentioned in the spec (Ethereum, Bitcoin, L2s) would appear as network pickers in a real wallet app."
        )

    # ----- Prediction / event contracts -----
    with st.expander("Event contracts / prediction markets (concept)", expanded=False):
        st.markdown(
            "Binary **yes/no** contracts on events — partnership-style integrations show **order book** elsewhere. "
            "Demo: pick an outcome."
        )
        st.radio("Example event", ["Fed cuts by June — Yes", "Fed cuts by June — No"], horizontal=True)

    # ----- Instant deposits -----
    with st.expander("Instant deposits (ACH buying power — illustrative caps)", expanded=False):
        lim = instant_deposit_limits(portfolio_total_usd)
        st.metric("Standard instant ACH (example cap)", f"${lim['standard_instant_ach_usd']:,.0f}")
        st.metric("Higher tier ceiling (example formula)", f"${lim['illustrative_tier_ceiling_usd']:,.0f}")
        st.caption("Uses your dashboard portfolio total as **portfolio_value** input — simplified vs real broker tiers.")

    # ----- Practice log -----
    with st.expander("Practice order log", expanded=False):
        log = st.session_state.get("practice_orders") or []
        if not log:
            st.info("No practice orders yet — submit from the order ticket expander.")
        else:
            st.dataframe(pd.DataFrame(log), use_container_width=True, hide_index=True)
