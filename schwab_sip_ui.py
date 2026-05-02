"""
Schwab Intelligent Portfolios (SIP) — Add-ons only.
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from schwab_sip_sim import (
    REBALANCE_DRIFT_THRESHOLD,
    SIP_ASSET_CLASS_BUCKETS_STORY,
    SIP_ETF_COUNT_STORY,
    SIP_MINIMUM_OPEN_USD,
    TLH_MIN_TAXABLE_USD,
    customizable_portfolio_story,
    income_focused_variant_story,
    investor_profile_review_story,
    equity_share,
    mock_estimated_tax_savings_ytd,
    municipal_bond_variant_story,
    profile_change_is_material,
    recommended_allocation,
    rebalance_story,
    risk_questionnaire_axes,
    schwab_personalized_indexing_story,
    sip_base_program_story,
    sip_premium_story,
    tlh_notification_bundle,
    tlh_sip_story,
    twenty_asset_class_reference,
    us_focused_variant_story,
)


def render_schwab_sip_addons() -> None:
    st.markdown("### Schwab Intelligent Portfolios (SIP) *(simulation)*")
    st.caption(
        f"Story numbers: **${SIP_MINIMUM_OPEN_USD:,}** minimum · **{SIP_ETF_COUNT_STORY}** ETFs · "
        f"**{SIP_ASSET_CLASS_BUCKETS_STORY}** sleeves · **{REBALANCE_DRIFT_THRESHOLD:.0%}** drift rebalance."
    )

    with st.expander("SIP — Base program", expanded=True):
        st.json(sip_base_program_story())

    with st.expander("Schwab Intelligent Portfolios Premium", expanded=False):
        st.json(sip_premium_story())

    with st.expander("Schwab Personalized Indexing (SPI)", expanded=False):
        st.json(schwab_personalized_indexing_story())

    with st.expander("Investor Profile Review (annual)", expanded=False):
        st.json(investor_profile_review_story())
        st.markdown("**Mini flow:** adjust answers vs last year's profile — see if change is **material**.")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Prior profile (story)**")
            old_rec = recommended_allocation(18.0, "Moderate", "Balanced", True)
            st.write(old_rec["rationale_plain_language"])
            old_w = old_rec["weights"]
            st.caption(f"Aggregate equity sleeves ≈ **{equity_share(old_w):.0%}**")
        with c2:
            st.markdown("**Updated answers**")
            hz2 = st.slider("New horizon (years)", 1.0, 40.0, 8.0, key="sip_hz2")
            lt2 = st.selectbox(
                "New loss tolerance",
                ["Conservative / low", "Moderate", "Aggressive / high"],
                index=1,
                key="sip_lt2",
            )
            new_rec = recommended_allocation(hz2, lt2, "Balanced", True)
            st.write(new_rec["rationale_plain_language"])
            new_w = new_rec["weights"]
            mat, delta = profile_change_is_material(old_w, new_w)
            st.caption(
                f"New aggregate equity ≈ **{equity_share(new_w):.0%}** · |Δ| ≈ **{delta:.1%}** — material if ≥ **{REBALANCE_DRIFT_THRESHOLD:.0%}**"
            )
        if mat:
            choice = st.radio(
                "New target proposed — choose whether to adopt",
                ["Confirm — rebalance to new target", "Reject — keep prior target until I edit again"],
                horizontal=True,
            )
            st.success(f"**Story outcome:** {choice.split('—')[0].strip()} recorded; trades queued only on confirm.")
        else:
            st.info("No **material** allocation shift in this toy example — annual review still logged (story).")

    with st.expander("Risk questionnaire & recommended allocation", expanded=False):
        st.json(risk_questionnaire_axes())
        c1, c2 = st.columns(2)
        with c1:
            hz = st.slider("Investment horizon (years)", 1.0, 40.0, 18.0)
            lt = st.selectbox(
                "Loss tolerance",
                ["Conservative / low", "Moderate", "Aggressive / high"],
            )
        with c2:
            goal = st.selectbox("Goal type", ["Growth", "Balanced", "Income", "Preserve capital"])
            inc_ok = st.checkbox("Income / cash-flow stability", value=True)
        rec = recommended_allocation(hz, lt, goal, inc_ok)
        st.info(rec["rationale_plain_language"])
        w = rec["weights"]
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=list(w.keys()),
                    values=list(w.values()),
                    hole=0.38,
                    textinfo="label+percent",
                )
            ]
        )
        fig.update_layout(height=420, title="Illustrative target mix (aggregated sleeves)")
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("Automatic portfolio rebalancing", expanded=False):
        tgt = recommended_allocation(15.0, "Moderate", "Balanced", True)["weights"]
        cur = {k: v + (0.08 if k == "US equity" else (-0.02 if k == "Cash" else 0.0)) for k, v in tgt.items()}
        s_cur = sum(cur.values())
        cur = {k: v / s_cur for k, v in cur.items()}
        rb = rebalance_story(cur, tgt)
        st.write(rb["threshold"])
        st.dataframe(pd.DataFrame(rb["drift_rows"]), use_container_width=True, hide_index=True)
        if rb["rebalance_required_story"]:
            st.warning("Drift example **triggers** internal rebalance (sim).")
        st.success(rb["user_notification"].replace("[date]", "**March 12, 2026**"))

    with st.expander(f"Automated tax-loss harvesting — taxable **${TLH_MIN_TAXABLE_USD:,}+**", expanded=False):
        tb = st.number_input("Taxable SIP balance ($)", value=85_000.0, step=5000.0)
        st.json(tlh_sip_story(tb))

    with st.expander("Tax-loss harvesting notifications & annual report", expanded=False):
        st.json(tlh_notification_bundle())
        st.json(mock_estimated_tax_savings_ytd())

    with st.expander("20 asset class diversification — plain English", expanded=False):
        st.dataframe(pd.DataFrame(twenty_asset_class_reference()), use_container_width=True, hide_index=True)

    with st.expander("Customizable SIP portfolios", expanded=False):
        st.json(customizable_portfolio_story())

    with st.expander("U.S.-Focused strategy option", expanded=False):
        st.json(us_focused_variant_story())

    with st.expander("Income-Focused strategy option", expanded=False):
        st.json(income_focused_variant_story())

    with st.expander("Municipal bond option (tax-efficient)", expanded=False):
        st.json(municipal_bond_variant_story())
