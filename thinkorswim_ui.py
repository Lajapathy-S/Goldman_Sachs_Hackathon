"""
thinkorswim platforms & tooling — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from thinkorswim_sim import (
    CHART_LAYOUTS_MAX_SAVE_STORY,
    TECHNICAL_STUDIES_COUNT_STORY,
    automated_strategy_builder_story,
    charts_navigator_story,
    economic_data_gadget_story,
    mock_trade_flash_rows,
    multichart_my_tools_story,
    oco_alerts_story,
    options_backtesting_story,
    papermoney_story,
    schwab_coaching_education_story,
    technical_studies_library_story,
    thinkorswim_desktop_story,
    thinkorswim_mobile_story,
    thinkorswim_web_story,
    thinkscript_story,
    trade_flash_story,
    volatility_probability_story,
    voice_command_trading_mobile_story,
    walk_limit_options_platforms_story,
    what_if_option_scenario,
)


def render_thinkorswim_addons() -> None:
    st.markdown("### thinkorswim® platforms *(spec simulation)*")
    st.caption("Schwab / thinkorswim naming is **illustrative** for coursework — not an official product demo.")

    with st.expander("thinkorswim Desktop — flagship downloadable platform", expanded=True):
        st.json(thinkorswim_desktop_story())

    with st.expander("thinkorswim Web — browser, core flows without install", expanded=False):
        st.json(thinkorswim_web_story())

    with st.expander("thinkorswim Mobile — charting, multi-leg, voice", expanded=False):
        mob = thinkorswim_mobile_story()
        st.metric("App Store rating (story)", f"{mob['app_store_rating_story']} / 5")
        st.json({k: v for k, v in mob.items() if k != "app_store_rating_story"})

    with st.expander("Voice Command Trading (Mobile)", expanded=False):
        st.json(voice_command_trading_mobile_story())
        st.caption("Try saying example phrases aloud on device — this web demo only shows the **story**.")

    with st.expander(f"{TECHNICAL_STUDIES_COUNT_STORY}+ technical studies & indicators", expanded=False):
        lib = technical_studies_library_story()
        st.markdown(f"**Size:** {lib['catalog_size_story']}")
        for cat, items in lib["categories"].items():
            with st.expander(cat):
                for it in items:
                    st.markdown(f"- {it}")
        st.caption(lib["scripted_extensions"])

    with st.expander("thinkScript™ — custom indicators & strategies", expanded=False):
        ts = thinkscript_story()
        st.markdown(
            f"- **{ts['language']}**\n"
            + "\n".join(f"- {c}" for c in ts["capabilities"])
            + f"\n- **Community:** {ts['community']}\n- **AI assist:** {ts['ai_assist']}"
        )
        st.code(ts["sample_snippet"], language="text")

    with st.expander("Schwab Coaching® Education (In-Platform)", expanded=False):
        st.json(schwab_coaching_education_story())

    st.markdown("#### Advanced tools, alerts & analytics *(spec)*")

    with st.expander("paperMoney® Virtual Trading", expanded=True):
        st.json(papermoney_story())

    with st.expander("Charts Navigator", expanded=False):
        st.json(charts_navigator_story())

    with st.expander(f"Multi-Chart Navigation — My Tools (up to {CHART_LAYOUTS_MAX_SAVE_STORY} layouts, desktop)", expanded=False):
        st.json(multichart_my_tools_story())

    with st.expander("Trade Flash (Real-Time Event Alerts)", expanded=False):
        st.json(trade_flash_story())
        st.dataframe(pd.DataFrame(mock_trade_flash_rows(8)), use_container_width=True, hide_index=True)

    with st.expander("One-Cancels-Other Alerts (OCO)", expanded=False):
        st.json(oco_alerts_story())

    with st.expander("Walk Limit® Orders (Options)", expanded=False):
        st.json(walk_limit_options_platforms_story())

    with st.expander("Options Back-Testing", expanded=False):
        st.json(options_backtesting_story())

    with st.expander("Volatility & Probability Analysis", expanded=False):
        st.json(volatility_probability_story())

    with st.expander("Economic Data Indicator Database", expanded=False):
        st.json(economic_data_gadget_story())

    with st.expander("What-If Scenario Analysis (Black-Scholes)", expanded=False):
        st.markdown(
            "Simulate **what-if** shocks on a hypothetical **European call** — spot, time to expiration, and IV. "
            "Illustrates platform-style analysis **without** exchange-grade margin or American exercise."
        )
        w1, w2, w3 = st.columns(3)
        with w1:
            spot = st.number_input("Spot / underlying", value=450.0)
            strike = st.number_input("Strike", value=455.0)
        with w2:
            t_years = st.number_input("Years to expiry", value=0.25, format="%.4f")
            iv = st.number_input("Implied vol (decimal)", value=0.22, format="%.4f")
        with w3:
            d_spot = st.number_input("Δ Spot", value=5.0)
            d_t_days = st.number_input("Δ Time (days)", value=-5.0)
            d_iv = st.number_input("Δ IV (decimal)", value=-0.02, format="%.4f")
        st.json(
            what_if_option_scenario(spot, strike, d_spot, t_years, d_t_days, iv, d_iv),
        )

    with st.expander("Automated Strategy Builder (AI-Assisted, in development)", expanded=False):
        st.json(automated_strategy_builder_story())
