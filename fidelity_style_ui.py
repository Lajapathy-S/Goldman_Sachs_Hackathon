"""
Fidelity-style brokerage add-ons (Add-ons tab) — simulation only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from fidelity_style_sim import (
    EXTENDED_AFTER_HOURS,
    EXTENDED_PRE_MARKET,
    FOREX_PAIRS,
    INTERNATIONAL_MARKETS,
    INTL_COMMISSION_NOTES,
    MARGIN_BASE_RATE_ANNUAL,
    MARGIN_PREMIUM_TIER_BALANCE_USD,
    MARGIN_PREMIUM_TIER_RATE,
    MINIMUM_OPEN_BALANCE_USD,
    MULTI_LEG_STRATEGIES,
    NTF_FUNDS_COUNT_ILLUSTRATIVE,
    OPTIONS_CONTRACT_FEE_USD,
    SLICE_MIN_USD,
    SLICE_UNIVERSE_NOTE,
    TOTAL_FUNDS_ACCESS_ILLUSTRATIVE,
    US_STOCK_ETF_COMMISSION_ONLINE,
    ZERO_EXPENSE_FUNDS,
    bond_cd_ladder,
    fractional_slice_from_dollars,
    margin_annual_interest,
    mock_bond_screener,
    mock_options_chain_extended,
)


def render_fidelity_brokerage_addons() -> None:
    st.markdown("### Fidelity-style brokerage suite *(simulation)*")
    st.warning(
        "**Not Fidelity.** Educational mirror of common brokerage capabilities — mock prices, schedules, and ladders."
    )

    # Stocks / ETFs US & international
    with st.expander("Commission-free US stocks & ETFs · international schedule", expanded=True):
        st.markdown(
            f"- **US online stock & ETF trades:** **${US_STOCK_ETF_COMMISSION_ONLINE:.0f}** commission (story).\n"
            f"- **Minimum to open:** **${MINIMUM_OPEN_BALANCE_USD:.0f}**.\n"
            "- **International equities:** separate commission schedule by market — examples below."
        )
        st.dataframe(pd.DataFrame(INTL_COMMISSION_NOTES), use_container_width=True, hide_index=True)

    # Options
    with st.expander(f"Options · ${OPTIONS_CONTRACT_FEE_USD:.2f}/contract (story) + multi-leg", expanded=False):
        st.caption("Greeks on chain; single and multi-leg strategies supported in full platforms.")
        st.markdown("**Multi-leg examples:** " + " · ".join(MULTI_LEG_STRATEGIES))
        n_leg = st.selectbox("Legs (illustrative)", [1, 2, 3, 4], index=1)
        fee = n_leg * OPTIONS_CONTRACT_FEE_USD
        st.metric("Illustrative per-trade contract fees (ex regulatory)", f"${fee:.2f}")
        st.dataframe(mock_options_chain_extended(7), use_container_width=True, hide_index=True)

    # Fractional
    with st.expander("Fractional shares (from $1) — “Stocks by the Slice”-style", expanded=False):
        st.markdown(
            f"**{SLICE_UNIVERSE_NOTE}** — minimum **${SLICE_MIN_USD:.0f}** notional (sim)."
        )
        ref = st.number_input("Reference price ($/share)", min_value=0.01, value=150.0, step=1.0)
        bucks = st.number_input("Dollar order", min_value=1.0, value=25.0, step=1.0)
        fr = fractional_slice_from_dollars(bucks, ref)
        st.json(fr)
        st.caption("Transferability of fractionals depends on firm & book position — story only here.")

    # Mutual funds
    with st.expander("Mutual funds — ZERO / NTF / same-day pricing", expanded=False):
        st.markdown(
            f"- **Universe (story):** **{TOTAL_FUNDS_ACCESS_ILLUSTRATIVE:,}+** funds.\n"
            f"- **0% expense** index funds (examples): **{', '.join(ZERO_EXPENSE_FUNDS)}**.\n"
            f"- **NTF (no transaction fee) story:** **{NTF_FUNDS_COUNT_ILLUSTRATIVE:,}+** funds from other managers.\n"
            "- **Same-day pricing** for most mutual fund trade stories — check prospectus in real life."
        )

    # Fixed income
    with st.expander("Fixed income — Treasuries, corporates, munis, agencies, CDs, money markets", expanded=False):
        st.markdown("**Bond screener (mock rows)** + BondSource-style **price discovery** is represented as a table only.")
        st.dataframe(mock_bond_screener(10), use_container_width=True, hide_index=True)

    # Margin
    with st.expander("Margin — tiered rates (illustrative)", expanded=False):
        st.markdown(
            f"Base rate story **~{MARGIN_BASE_RATE_ANNUAL * 100:.2f}%**; "
            f"**{MARGIN_PREMIUM_TIER_RATE * 100:.2f}%** for balances **${MARGIN_PREMIUM_TIER_BALANCE_USD/1e6:.1f}M+** narrative."
        )
        bor = st.number_input("Borrowed on margin ($)", min_value=0.0, value=25000.0, step=1000.0)
        eq = st.number_input("Account equity proxy for tier ($)", min_value=0.0, value=50000.0, step=5000.0)
        st.json(margin_annual_interest(bor, eq))

    # Forex
    with st.expander("Forex — spot FX via spread (story)", expanded=False):
        st.caption(f"**{len(FOREX_PAIRS)}** pairs shown — commission modeled as **spread**, not per-trade dollars.")
        st.multiselect("Pairs (subset)", FOREX_PAIRS, default=FOREX_PAIRS[:6])

    # International stocks
    with st.expander("International stocks — 25+ markets", expanded=False):
        st.metric("Illustrative markets supported", len(INTERNATIONAL_MARKETS))
        st.dataframe(pd.DataFrame({"Market": INTERNATIONAL_MARKETS}), use_container_width=True, hide_index=True)

    # Recurring / DCA
    with st.expander("Automated recurring investments / DCA", expanded=False):
        st.selectbox("Frequency", ["Weekly", "Bi-weekly", "Monthly"], index=2)
        st.text_input("Symbol or fund (mock)", value="VTI")
        st.number_input("Amount ($)", min_value=1.0, value=100.0, step=10.0)
        st.success("Schedule stored **in-session only** — no orders executed.")

    # Extended hours
    with st.expander("Extended hours — limits only", expanded=False):
        st.markdown(
            f"- **Pre-market:** {EXTENDED_PRE_MARKET}\n"
            f"- **After-hours:** {EXTENDED_AFTER_HOURS}\n"
            "- **Limit orders** typically required outside regular session (story)."
        )

    # IPO
    with st.expander("New-issue IPOs & secondary offerings", expanded=False):
        st.info(
            "Eligible customers participate via allocation process described in account docs — **no allocation logic** here."
        )

    # Ladder
    with st.expander("CD & Treasury laddering tool", expanded=False):
        tot = st.number_input("Total principal ($)", min_value=1000.0, value=100000.0, step=5000.0)
        rungs = st.slider("Number of rungs", 3, 12, 6)
        span = st.slider("Years spanned", 1.0, 15.0, 6.0)
        yld = st.slider("Assumed annual yield (mock %)", 1.0, 8.0, 4.5) / 100.0
        st.dataframe(bond_cd_ladder(tot, rungs, span, yld), use_container_width=True, hide_index=True)
        st.caption("Visual maturity timeline would be a Gantt-style chart in production — table stands in for demo.")
