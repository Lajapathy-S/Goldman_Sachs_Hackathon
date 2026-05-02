"""
Optional features layered on top of the core app.

Keep portfolio_logic, holdings/scenarios flows, and existing tabs unchanged.
Add new UI here (and companion *_sim.py modules), then call render helpers from
`render_custom_features_tab()` below.
"""

from __future__ import annotations

import streamlit as st

from core_trading_ui import render_core_trading_addons
from schwab_extended_ui import render_schwab_extended_addons
from thinkorswim_ui import render_thinkorswim_addons
from financial_addons_ui import render_financial_addons
from fidelity_portfolio_hub_ui import render_fidelity_portfolio_hub_addons
from retirement_planning_ui import render_retirement_planning_addons
from schwab_retirement_accounts_ui import render_schwab_retirement_accounts_addons
from specialty_accounts_ui import render_specialty_accounts_addons
from research_education_ui import render_research_education_addons
from robo_advisory_ui import render_robo_advisory_addons
from schwab_sip_ui import render_schwab_sip_addons
from schwab_wealth_ui import render_schwab_wealth_addons
from schwab_banking_ui import render_schwab_banking_addons
from schwab_research_ui import render_schwab_research_addons
from fidelity_style_ui import render_fidelity_brokerage_addons
from trader_plus_ui import render_trader_plus_addons


def render_custom_features_tab() -> None:
    """Entry point for all incremental features — safe extension surface."""
    st.subheader("Add-ons")
    st.caption(
        "Stack **new** experiments here. Core tabs (**Dashboard**, **Goals**, **What-if**, etc.) stay as-is."
    )

    with st.expander("How we extend without breaking the base", expanded=False):
        st.markdown(
            "1. Add logic in a **new** file (e.g. `my_feature_sim.py`).\n"
            "2. Add UI in a **new** file or function.\n"
            "3. Import and call it **only** from this module under `render_custom_features_tab`.\n"
            "4. Avoid editing `portfolio_logic.py` unless you intend to change shared analytics."
        )

    render_fidelity_brokerage_addons()

    render_trader_plus_addons()

    render_core_trading_addons()

    render_schwab_extended_addons()

    render_thinkorswim_addons()

    render_fidelity_portfolio_hub_addons()

    render_robo_advisory_addons()

    render_schwab_sip_addons()

    render_schwab_wealth_addons()

    render_schwab_banking_addons()

    render_schwab_research_addons()

    render_research_education_addons()

    render_financial_addons()

    render_retirement_planning_addons()

    render_schwab_retirement_accounts_addons()

    render_specialty_accounts_addons()

    _placeholder_section()


def _placeholder_section() -> None:
    with st.expander("More add-ons (stack here)", expanded=False):
        st.info(
            "Additional specs can add new `render_*()` calls above this expander in "
            "`render_custom_features_tab` — core tabs stay untouched."
        )


# --- Hook: import and call additional sections below, e.g. ---
# from alerts_ui import render_smart_alerts
# render_smart_alerts()
