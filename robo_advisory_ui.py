"""
§2.4 Robo-advisory & managed accounts — Add-ons tab only.
"""

from __future__ import annotations

import streamlit as st

from portfolio_logic import portfolio_total
from robo_advisory_sim import (
    FLEX_FUNDS_NOTE,
    GO_ENHANCED_MIN_USD,
    GO_MINIMUM_FIRST_INVESTMENT,
    GO_ZERO_FEE_CAP_USD,
    KIPLINGER_AWARD_STORY,
    SMA_MIN_USD,
    WEALTH_MANAGEMENT_MIN_USD,
    WEALTH_SERVICES_MIN_USD,
    go_fee_story,
    managed_account_tier,
    model_portfolio_catalog,
    sma_strategies_table,
    wealth_fee_illustrative,
)


def render_robo_advisory_addons() -> None:
    ss = st.session_state
    invested = portfolio_total(ss.holdings)
    cash = float(ss.get("cash_balance_usd") or 0.0)
    ss.setdefault("ra_external_aum", 0.0)
    ss.setdefault("ra_go_review_done", False)

    total_for_tiers = invested + cash + float(ss.ra_external_aum)
    bal_demo = st.number_input(
        "Investable assets for tier simulation ($)",
        min_value=0.0,
        value=float(total_for_tiers if total_for_tiers > 0 else 15_000),
        step=1000.0,
        key="ra_bal_demo",
        help="Defaults to holdings + cash + external link; edit to explore tiers.",
    )
    ss.ra_external_aum = float(
        st.number_input(
            "External / linked assets included in story ($)",
            min_value=0.0,
            value=float(ss.ra_external_aum),
            step=5000.0,
            key="ra_ext",
        )
    )
    total_for_tiers = invested + cash + ss.ra_external_aum
    st.caption(f"Computed total (holdings + cash + external): **${total_for_tiers:,.0f}** — demo input uses **${bal_demo:,.0f}**.")

    st.markdown("### Robo-advisory & managed accounts *(§2.4 simulation)*")
    st.caption("Program descriptions mirror common industry tiers — **not** an offer of advisory services.")

    # ----- Fidelity Go -----
    with st.expander("Fidelity Go (robo-advisor)", expanded=True):
        st.markdown(
            f"- **Zero program fee** for balances **under ${GO_ZERO_FEE_CAP_USD:,.0f}** (story).\n"
            f"- **Start from ${GO_MINIMUM_FIRST_INVESTMENT:.0f}**.\n"
            f"- **Auto-invest** in **Fidelity Flex** funds — {FLEX_FUNDS_NOTE}\n"
            "- **Annual review** prompt for life changes.\n"
            f"- **Award:** {KIPLINGER_AWARD_STORY}"
        )
        st.json(go_fee_story(bal_demo))
        ss.ra_go_review_done = st.checkbox(
            "Complete annual Go review checklist (sim)",
            value=bool(ss.ra_go_review_done),
        )

    # ----- Go enhanced -----
    with st.expander(f"Go — Personalized Planning & Advice (${GO_ENHANCED_MIN_USD:,.0f}+)", expanded=False):
        if bal_demo >= GO_ENHANCED_MIN_USD:
            st.success(
                "**Enhanced tier (story):** unlimited **one-on-one coaching** sessions — "
                "no incremental fee above standard Go pricing narrative."
            )
        else:
            st.info(f"Raise demo balance to **${GO_ENHANCED_MIN_USD:,.0f}+** to unlock coaching storyline.")

    # ----- Wealth Services / Management -----
    with st.expander("Fidelity Wealth Services & Wealth Management (human advice)", expanded=False):
        st.markdown(
            f"- **Wealth Services:** discretionary management **${WEALTH_SERVICES_MIN_USD:,.0f}+** — dedicated advisor & plan.\n"
            f"- **Wealth Management:** **${WEALTH_MANAGEMENT_MIN_USD:,.0f}+** — tax, estate, insurance, team coverage."
        )
        st.markdown(wealth_fee_illustrative(bal_demo, "fws"))
        st.markdown(wealth_fee_illustrative(bal_demo, "fwm"))

    # ----- SMA -----
    with st.expander(f"Fidelity Strategic Disciplines (SMA · ${SMA_MIN_USD:,.0f}+)", expanded=False):
        st.dataframe(sma_strategies_table(), use_container_width=True, hide_index=True)
        st.caption("Direct ownership of securities for tax control — allocation overlays differ by sleeve.")

    # ----- Model portfolios -----
    with st.expander("Model Portfolio Center", expanded=False):
        st.markdown(
            "Pre-built models from **conservative** through **aggressive growth** — **ETF** or **mutual fund** implementations."
        )
        st.dataframe(model_portfolio_catalog(), use_container_width=True, hide_index=True)
        st.selectbox("Start from model", ["Conservative", "Moderate", "Growth", "Aggressive growth"])
        st.caption("Self-directed investors use models as templates — orders not placed here.")

    # ----- Eligibility snapshot -----
    with st.expander("Eligibility snapshot (computed total)", expanded=False):
        st.metric("Holdings + cash + external", f"${total_for_tiers:,.0f}")
        for line in managed_account_tier(total_for_tiers)["service_lines"]:
            st.markdown(f"- {line}")
        st.caption(managed_account_tier(total_for_tiers)["next_review"])
