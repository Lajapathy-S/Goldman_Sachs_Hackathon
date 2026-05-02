"""
Fidelity portfolio hub — planning & guidance add-ons (Add-ons tab only).
"""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from fidelity_portfolio_hub_sim import (
    GOAL_TYPES,
    annual_checkup_items,
    asset_class_breakdown,
    concentration_flags,
    drift_vs_target,
    external_accounts_template,
    gain_loss_report_plaintext,
    gain_loss_table,
    monte_carlo_goal_success,
    retirement_monthly_income_story,
    retirement_savings_adjustment_hint,
    sector_stub_within_equity,
    tax_center_ytd_mock,
    tax_loss_candidates,
)
from portfolio_logic import portfolio_total, profile_from_onboarding
from portfolio_mgmt_ui import ensure_portfolio_state


def render_fidelity_portfolio_hub_addons() -> None:
    ss = st.session_state
    ensure_portfolio_state(ss)
    ss.setdefault("fp_ira", 42000.0)
    ss.setdefault("fp_401k", 88000.0)
    ss.setdefault("fp_hsa", 9200.0)
    ss.setdefault("fp_manual_home", 380000.0)
    ss.setdefault("fp_manual_car", 18500.0)
    ss.setdefault("fp_go_rebalance_log", [])
    profile = profile_from_onboarding(ss.onboarding) if ss.onboarding else None

    st.markdown("### Portfolio hub & guidance *(Fidelity-style simulation)*")
    st.caption(
        "**§2.3 Portfolio management & financial planning** — holistic planning UI; **mock** data and math; "
        "not personalized advice."
    )

    invested = portfolio_total(ss.holdings)
    cash = float(ss.get("cash_balance_usd") or 0.0)
    crypto = float(ss.get("crypto_holdings_usd") or 0.0)
    total_all = invested + cash + crypto + float(ss.fp_ira) + float(ss.fp_401k) + float(ss.fp_hsa)

    # ----- Overview dashboard -----
    with st.expander("Portfolio overview dashboard (consolidated accounts)", expanded=True):
        ss.fp_ira = float(st.number_input("IRA balance ($, sim)", value=float(ss.fp_ira), step=1000.0, key="fp_ira"))
        ss.fp_401k = float(st.number_input("401(k) balance ($, sim)", value=float(ss.fp_401k), step=1000.0, key="fp401"))
        ss.fp_hsa = float(st.number_input("HSA balance ($, sim)", value=float(ss.fp_hsa), step=500.0, key="fp_hsa"))

        total_all = invested + cash + crypto + ss.fp_ira + ss.fp_401k + ss.fp_hsa
        demo_change = (hash(str(ss.holdings)) % 200 - 100) / 10.0
        m1, m2 = st.columns(2)
        m1.metric("Total investable (story)", f"${total_all:,.0f}", f"{demo_change:+.2f}% today (sim)")
        m2.metric("Core app holdings only", f"${invested:,.0f}")

        if ss.holdings:
            top = sorted(ss.holdings, key=lambda h: float(h.get("value", 0) or 0), reverse=True)[:5]
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=[h.get("name", "")[:22] for h in top],
                        values=[float(h.get("value", 0) or 0) for h in top],
                        hole=0.45,
                    )
                ]
            )
            fig.update_layout(height=320, title="Top holdings (from core holdings)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add holdings on **My holdings** for a richer donut.")

    # Proactive insights
    with st.expander("Proactive portfolio insights", expanded=False):
        for msg in concentration_flags(ss.holdings):
            st.markdown(f"- {msg}")

    # Planning & Monte Carlo
    with st.expander("Planning & Guidance Center — goals & Monte Carlo", expanded=False):
        st.multiselect(
            "Goal types (story)",
            list(GOAL_TYPES),
            default=["Retirement"],
            help="Retirement, college, home, emergency fund — tied to models below.",
        )
        st.multiselect(
            "Assign to accounts (sim)",
            ["Brokerage (core app)", "IRA", "401(k)", "HSA"],
            default=["Brokerage (core app)", "IRA"],
            help="Which sleeves fund this goal — labels only in prototype.",
        )
        g_goal = st.number_input("Goal wealth ($)", min_value=0.0, value=750000.0, step=10000.0)
        g_years = st.slider("Years to goal", 3.0, 40.0, 18.0)
        g_init = st.number_input("Starting assets ($)", min_value=0.0, value=float(invested or 50000), step=5000.0)
        g_monthly = st.number_input("Monthly contribution ($)", min_value=0.0, value=800.0, step=50.0)
        if st.button("Run Monte Carlo (toy)"):
            prob, dist = monte_carlo_goal_success(
                goal_wealth=g_goal,
                years=g_years,
                initial=g_init,
                monthly_contribution=g_monthly,
            )
            st.metric("Integrated probability of success (sim)", f"{prob * 100:.1f}%")
            st.caption(
                f"Monte Carlo: **400** toy paths; mean ending wealth ≈ ${dist.mean():,.0f}. "
                "Not a forecast — illustration only."
            )

    # Retirement income
    with st.expander("Retirement income projector", expanded=False):
        c_a, c_b, c_c = st.columns(3)
        with c_a:
            cur_age = st.number_input("Current age", min_value=18, max_value=95, value=42)
        with c_b:
            ret_age = st.number_input("Planned retirement age", min_value=50, max_value=80, value=65)
        with c_c:
            inc = st.number_input("Annual income ($, story)", min_value=0.0, value=95000.0, step=1000.0)
        sv_rate = st.slider("Current savings rate (% of income)", 0.0, 40.0, 12.0)
        implied_monthly_save = inc * (sv_rate / 100.0) / 12.0
        st.caption(f"Implied monthly savings at **{sv_rate:.1f}%**: **${implied_monthly_save:,.0f}** (illustrative).")

        nest = st.number_input("Nest egg at retirement ($)", min_value=0.0, value=float(invested + ss.fp_401k), step=5000.0)
        wr = st.slider("Annual withdrawal rate (story)", 0.02, 0.06, 0.04)
        ss_est = st.number_input("Social Security monthly ($)", min_value=0.0, value=2400.0, step=100.0)
        ri = retirement_monthly_income_story(
            nest_egg=nest, withdrawal_rate=wr, social_security_monthly=ss_est
        )
        st.json(ri)
        need = st.number_input("Monthly need ($)", min_value=0.0, value=8500.0, step=100.0)
        gap = need - ri["total_monthly_estimate"]
        st.metric("Gap vs need (sim)", f"${gap:+,.0f}/mo")
        yrs_left = max(1.0, float(ret_age - cur_age))
        adj = retirement_savings_adjustment_hint(gap, yrs_left)
        if gap > 0:
            st.info(
                f"**Savings adjustment hint:** consider raising contributions by about "
                f"**${adj['suggested_extra_monthly_save']:,.0f}/mo** over the next ~{yrs_left:.0f} years (toy math). "
                f"{adj['note']}"
            )

    # Tax-loss harvesting
    with st.expander("Tax-loss harvesting (Tax-Smart Investing story)", expanded=False):
        st.dataframe(tax_loss_candidates(ss.holdings), use_container_width=True, hide_index=True)
        st.caption("Wash-sale and substitute funds must follow IRS rules — teaching stub only.")

    # Full view / aggregation
    with st.expander("Full View — external aggregation (Plaid / Yodlee story)", expanded=False):
        st.dataframe(external_accounts_template(), use_container_width=True, hide_index=True)
        st.caption("Live linking would use Plaid/Yodlee — static mock rows here.")

    # Net worth
    with st.expander("Net worth & trend (manual assets + liabilities via Full View)", expanded=False):
        ss.fp_manual_car = float(
            st.number_input("Manual vehicle value ($)", value=float(ss.fp_manual_car), step=1000.0, key="fp_car")
        )
        ss.fp_manual_home = float(
            st.number_input("Manual real estate ($)", value=float(ss.fp_manual_home), step=10000.0, key="fp_home")
        )
        ext_df = external_accounts_template()
        nw = total_all + ss.fp_manual_home + ss.fp_manual_car + float(ext_df["Balance"].sum())
        st.metric("Holistic net worth (sim components)", f"${nw:,.0f}")
        trend = pd.Series([nw * (0.92 + i * 0.02) for i in range(6)])
        figt = go.Figure(go.Scatter(y=trend.values, x=list(range(len(trend))), mode="lines+markers"))
        figt.update_layout(height=260, title="Net worth trend (illustrative)")
        st.plotly_chart(figt, use_container_width=True)

    # Fidelity Go auto rebalance
    with st.expander("Automatic rebalancing (Fidelity Go story)", expanded=False):
        if st.button("Simulate drift rebalance notification"):
            ss.fp_go_rebalance_log.append("Portfolio rebalanced to target mix — notification sent (sim).")
        for line in ss.fp_go_rebalance_log[-5:]:
            st.success(line)

    # Asset allocation vs target
    with st.expander("Asset allocation analysis — drift vs target", expanded=False):
        drift_df = drift_vs_target(profile, ss.holdings)
        if "Drift status" in drift_df.columns:
            st.markdown("**Color-coded drift:** *On track* · *Watch* · *Review* (labels).")
            st.dataframe(drift_df, use_container_width=True, hide_index=True)
        else:
            st.dataframe(drift_df, use_container_width=True, hide_index=True)
        ac = asset_class_breakdown(ss.holdings)
        st.markdown("**Actual sleeves ($)**")
        st.dataframe(ac, use_container_width=True, hide_index=True)
        if profile:
            st.markdown(
                f"**Underlying Goals mix (growth / balanced / stable):** "
                f"{profile.growth_target_pct:.0f}% / {profile.balanced_target_pct:.0f}% / {profile.stable_target_pct:.0f}%"
            )
        sec = sector_stub_within_equity(ss.holdings)
        if not sec.empty:
            st.markdown("**Sector mix (equity sleeve — toy)**")
            st.dataframe(sec, use_container_width=True, hide_index=True)

    # G/L report
    with st.expander("Realized & unrealized gain/loss report", expanded=False):
        gl = gain_loss_table(ss.holdings)
        if gl.empty:
            st.caption("No positions.")
        else:
            st.dataframe(gl, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV",
                gl.to_csv(index=False),
                file_name="gain_loss_sim.csv",
                mime="text/csv",
            )
            st.download_button(
                "Download printable report (plain text — save/print as PDF)",
                gain_loss_report_plaintext(gl),
                file_name="gain_loss_report_sim.txt",
                mime="text/plain",
                key="dl_gl_txt",
            )
            st.caption("Daily-after-close refresh in production — export is **end-of-session snapshot** here.")

    # Tax Center
    with st.expander("Tax Center (year-round)", expanded=False):
        st.json(tax_center_ytd_mock())
        st.caption("TurboTax integration would pipe 1099 data — mock totals only.")

    # Annual checkup
    with st.expander("Annual Financial Checkup", expanded=False):
        for i, (title, hint) in enumerate(annual_checkup_items()):
            st.checkbox(f"**{title}** — {hint}", value=False, key=f"fp_chk_{i}")
