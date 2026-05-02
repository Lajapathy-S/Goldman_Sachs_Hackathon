"""
§3.1 Core trading features — Add-ons only (spec showcase; does not replace Trading tab).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core_trading_sim import (
    OPTION_FEE_PER_CONTRACT,
    SP500_SAMPLE_TICKERS,
    STOCK_SLICE_MIN_USD,
    STOCK_SLICES_MAX_NAMES,
    commission_schedule_summary,
    estimate_options_commission,
    fixed_income_story_box,
    forex_panel_story,
    futures_universe_story,
    mock_bondsource_rows,
    validate_stock_slices,
    walk_limit_story,
)


def render_core_trading_addons() -> None:
    st.markdown("### Core trading features *(§3.1 simulation)*")
    st.caption("Pricing and product scope are **story-level** — not a live broker integration.")

    # Commission-free equities + options fee
    with st.expander("Commission-free stock & ETF trading · options per-contract fee", expanded=True):
        st.json(commission_schedule_summary())
        st.markdown(
            f"- **US stocks & ETFs (online):** **$0** commission.\n"
            f"- **Options:** **${OPTION_FEE_PER_CONTRACT:.2f}** per contract.\n"
            "- **Account minimum:** none · **Inactivity / maintenance:** none (story)."
        )
        oc1, oc2 = st.columns(2)
        with oc1:
            legs = st.number_input("Option legs", min_value=1, max_value=8, value=1)
            ctr = st.number_input("Contracts per leg", min_value=0.0, value=10.0, step=1.0)
        with oc2:
            st.json(estimate_options_commission(ctr, int(legs)))

    # Stock Slices
    with st.expander("Fractional investing — Stock Slices (S&P 500 names from $5)", expanded=False):
        st.markdown(
            f"Up to **{STOCK_SLICES_MAX_NAMES}** names per order; **${STOCK_SLICE_MIN_USD:g}** minimum per slice — commission-free (story)."
        )
        picks = st.multiselect(
            "Symbols (sample S&P 500 list)",
            SP500_SAMPLE_TICKERS,
            default=SP500_SAMPLE_TICKERS[:3],
            max_selections=STOCK_SLICES_MAX_NAMES,
        )
        amounts: list[tuple[str, float]] = []
        if picks:
            st.markdown("**Dollar amount per slice**")
            cols = st.columns(min(4, len(picks)))
            for i, sym in enumerate(picks):
                with cols[i % len(cols)]:
                    amt = st.number_input(sym, min_value=0.0, value=max(STOCK_SLICE_MIN_USD, 25.0), step=1.0, key=f"sl_{sym}")
                    amounts.append((sym, amt))
        if amounts:
            v = validate_stock_slices(amounts)
            if v["valid"]:
                st.success(f"Basket notional **${v['notional_total']:,.2f}** across **{v['line_count']}** slices (sim validation).")
            else:
                for e in v["errors"]:
                    st.error(e)

    # Options + Walk Limit
    with st.expander("Options trading — Walk Limit® (thinkorswim story)", expanded=False):
        st.markdown(
            "**Single- and multi-leg** strategies supported on platform (story). "
            "**Walk Limit®** gradually adjusts your working limit to improve fill probability without aggressively lifting through the spread."
        )
        w1, w2, w3, w4 = st.columns(4)
        with w1:
            bid = st.number_input("Bid", value=2.45, format="%.4f")
        with w2:
            ask = st.number_input("Ask", value=2.52, format="%.4f")
        with w3:
            mid = st.number_input("Mid (ref)", value=(2.45 + 2.52) / 2, format="%.4f")
        with w4:
            agg = st.slider("Walk aggressiveness", 0.0, 1.0, 0.35, 0.05)
        st.json(walk_limit_story(mid, bid, ask, agg))

    # Futures
    with st.expander("Futures trading — thinkorswim", expanded=False):
        st.json(futures_universe_story())

    # Forex
    with st.expander("Forex trading — thinkorswim", expanded=False):
        fx = forex_panel_story()
        st.markdown(
            f"**{fx['pairs_available_story']}** currency pairs · **{fx['pricing']}** · **{fx['hours']}**"
        )
        st.write("Sample watchlist:", ", ".join(fx["sample_watchlist"]))
        st.caption(f"Illustrative spread floor ~{fx['sample_spread_pips']} pips on majors (story).")

    # Fixed income
    with st.expander("Fixed income — bonds, CDs, Treasuries (BondSource™ story)", expanded=False):
        st.json(fixed_income_story_box())
        st.dataframe(pd.DataFrame(mock_bondsource_rows(12)), use_container_width=True, hide_index=True)
        st.caption("Bid/ask grid is **mock** — BondSource™ shows live inventory in production.")
