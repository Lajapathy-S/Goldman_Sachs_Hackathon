"""
AIChemist — beginner-friendly stock & mutual fund portfolio view (Streamlit).
"""

from __future__ import annotations

import copy

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from cortex_ui import render_cortex_research_tab
from gold_ui import render_gold_tab
from banking_ui import render_banking_tab
from custom_features_ui import render_custom_features_tab
from social_ui import render_social_tab
from legend_ui import render_legend_tab
from portfolio_mgmt_sim import holding_mock_price_ticker
from portfolio_mgmt_ui import (
    ensure_portfolio_state,
    patch_demo_for_accounts,
    render_unified_portfolio_dashboard,
)
from trading_ui import render_trading_sim_tab

from portfolio_logic import (
    BUCKET_LABELS,
    BUCKET_MARKET_SENSITIVITY,
    SCENARIOS,
    allocation_df,
    allocation_pcts,
    annual_fee_drag,
    health_score,
    holdings_to_buckets,
    portfolio_total,
    profile_from_onboarding,
    recommend_for_scenario,
)

st.set_page_config(
    page_title="AIChemist — Simple Portfolio Care",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Session defaults ---
if "holdings" not in st.session_state:
    st.session_state.holdings = []
if "onboarding" not in st.session_state:
    st.session_state.onboarding = None
if "welcome_dismissed" not in st.session_state:
    st.session_state.welcome_dismissed = False

ensure_portfolio_state(st.session_state)


def display_type(raw: str) -> str:
    return {"mutual_fund": "Mutual fund", "stock": "Stock"}.get(raw, raw)


def init_demo_portfolio():
    patch_demo_for_accounts(st.session_state)
    st.session_state.onboarding = {
        "goal": "Grow wealth over time",
        "horizon": "5–10 years",
        "comfort": "A moderate dip (around 15%) is stressful but okay",
    }


def risk_meter_value(holdings, _profile):
    if portfolio_total(holdings) <= 0:
        return 0, "neutral"
    p = allocation_pcts(holdings)
    growth_share = p["growth"] / 100.0
    # Simple 0-100 "risk" dial: more growth => higher meter
    raw = int(round(growth_share * 100))
    if raw < 35:
        tone = "low"
    elif raw < 60:
        tone = "moderate"
    else:
        tone = "higher"
    return raw, tone


def fig_allocation_pie(holdings):
    buckets = holdings_to_buckets(holdings)
    labels = [BUCKET_LABELS[k] for k in buckets if buckets[k] > 0]
    values = [buckets[k] for k in buckets if buckets[k] > 0]
    if not values:
        return None
    colors = {"growth": "#2ecc71", "balanced": "#3498db", "stable": "#95a5a6"}
    ckeys = [k for k in buckets if buckets[k] > 0]
    pie_colors = [colors[k] for k in ckeys]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.45,
                marker=dict(colors=pie_colors),
                textinfo="label+percent",
            )
        ]
    )
    fig.update_layout(
        margin=dict(t=30, b=30, l=30, r=30),
        showlegend=True,
        legend_orientation="h",
        legend_yanchor="bottom",
        legend_y=-0.2,
        height=380,
    )
    return fig


def fig_health_gauge(score: int):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Portfolio health"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#27ae60"},
                "steps": [
                    {"range": [0, 40], "color": "#fadbd8"},
                    {"range": [40, 70], "color": "#fdebd0"},
                    {"range": [70, 100], "color": "#d5f5e3"},
                ],
                "threshold": {
                    "line": {"color": "black", "width": 2},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(height=280, margin=dict(l=40, r=40, t=40, b=20))
    return fig


# --- Sidebar ---
with st.sidebar:
    st.title("🌱 AIChemist")
    st.caption("Plain-language investing — stocks & mutual funds in one calm place.")
    if st.button("Load example portfolio", type="secondary"):
        init_demo_portfolio()
        st.rerun()
    st.divider()
    st.markdown("**Why this exists**")
    st.markdown(
        "Markets feel noisy. This tool helps you **see what you own**, "
        "**match money to your life**, and think through **simple what-if** moves — "
        "without jargon or overwhelming tables."
    )
    st.divider()
    st.markdown("**Quick path**")
    st.markdown(
        "1. **My holdings** — add what you own (names only; no ticker stress).\n"
        "2. **Goals & profile** — tell us your timeline and how drops feel.\n"
        "3. **What-if scenarios** — see plain-language moves + sample dollar amounts.\n"
        "4. **Research & AI (sim)** — Cortex-style digests, screeners, and Gold-tier mocks.\n"
        "5. **Gold (sim)** — subscription story, IRA match, cash APY, margin, Strategies fees.\n"
        "6. **Banking (sim)** — Gold banking, card, RVI, IRA tools (mock).\n"
        "7. **Legend (sim)** — pro charts, ladder, option P&L, futures panel.\n"
        "8. **Trading (sim)** — order types, fractionals, and other flows **without real money**.\n"
        "9. **Social (sim)** — feed, sharing card, referrals (mock).\n"
        "10. **Add-ons** — stack new features without changing core tabs."
    )
    st.caption("Tip: use **Load example portfolio** to explore before typing anything.")
    avg_fee = st.number_input(
        "Guess your yearly fund fee (weighted average %)",
        min_value=0.0,
        max_value=3.0,
        value=0.50,
        step=0.05,
        help="From fund factsheets: expense ratio. Used only to show a rough yearly cost — not exact.",
    )
    st.session_state["weighted_expense_pct"] = avg_fee


profile = (
    profile_from_onboarding(st.session_state.onboarding)
    if st.session_state.onboarding
    else None
)

tab_dash, tab_holdings, tab_goals, tab_scenarios, tab_research, tab_gold, tab_banking, tab_legend, tab_trade, tab_social, tab_addons = st.tabs(
    [
        "Dashboard",
        "My holdings",
        "Goals & profile",
        "What-if scenarios",
        "Research & AI (sim)",
        "Gold (sim)",
        "Banking (sim)",
        "Legend (sim)",
        "Trading (sim)",
        "Social (sim)",
        "Add-ons",
    ]
)

# ----- Dashboard -----
with tab_dash:
    render_unified_portfolio_dashboard(profile)

    if not st.session_state.welcome_dismissed:
        with st.container():
            b1, b2 = st.columns([4, 1])
            with b1:
                st.success(
                    "**Welcome.** Nothing here predicts the future — it organizes what you own, "
                    "matches it to your life, and turns scary headlines into **small, understandable steps**."
                )
            with b2:
                if st.button("Dismiss", key="dismiss_welcome"):
                    st.session_state.welcome_dismissed = True
                    st.rerun()

    st.subheader("Your unified snapshot")
    total = portfolio_total(st.session_state.holdings)
    fee_pct = float(st.session_state.get("weighted_expense_pct") or 0.5)
    yearly_fees = annual_fee_drag(total, fee_pct)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Total value (what you entered)",
            f"${total:,.0f}",
            help="Your latest approximate value — update when you like.",
        )
    score, health_msg = health_score(st.session_state.holdings, profile)
    with c2:
        st.metric(
            "How well your mix fits you",
            f"{score}/100",
            help="Blends diversification with how close you are to the target mix from Goals — not a grade on you.",
        )
    rv, tone = risk_meter_value(st.session_state.holdings, profile)
    with c3:
        label = (
            "Ups & downs exposure"
            if tone == "neutral"
            else f"Ups & downs — {tone} growth tilt"
        )
        st.metric(
            label,
            f"{rv}/100" if total > 0 else "—",
            help="Higher means more of your money rides on growth-style investments (which swing more). Not 'good' or 'bad' by itself.",
        )
    with c4:
        st.metric(
            "Your profile",
            (profile.label[:28] + "…")
            if profile and len(profile.label) > 28
            else (profile.label if profile else "Not set"),
            help="From **Goals & profile** — timeline and how you feel about drops.",
        )

    if total > 0:
        st.caption(
            f"Rough yearly fund costs at **{fee_pct:.2f}%** of assets: about **${yearly_fees:,.0f}/year** "
            "(illustrative — check each fund’s expense ratio)."
        )

    if profile:
        st.info(health_msg)
    else:
        st.warning(health_msg)

    if total <= 0:
        st.markdown(
            "Add holdings under **My holdings** or click **Load example portfolio** in the sidebar."
        )
    else:
        g1, g2 = st.columns((1.1, 1))
        with g1:
            fig_pie = fig_allocation_pie(st.session_state.holdings)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
        with g2:
            st.plotly_chart(fig_health_gauge(score), use_container_width=True)

        st.markdown("#### Your mix vs. the mix we suggested for you")
        df_alloc = allocation_df(st.session_state.holdings, profile)
        st.dataframe(
            df_alloc,
            use_container_width=True,
            hide_index=True,
        )
        with st.expander("What do these rows mean?"):
            st.markdown(
                "**Growth** = mostly stocks and stock-heavy funds. **Balanced** = mixed stock/bond funds. "
                "**Stable** = bonds, cash-like, shorter-term. "
                "“Target” comes from your answers — a compass, not a rule from Wall Street."
            )

# ----- Holdings -----
with tab_holdings:
    st.subheader("What you own")
    st.caption(
        "Use simple names you recognize. We sort each line into **growth**, **balanced**, or **stable** "
        "based on what you pick — no ticker symbols required."
    )

    with st.expander("Add or edit a holding", expanded=not st.session_state.holdings):
        ensure_portfolio_state(st.session_state)
        acc_opts = st.session_state.accounts
        acc_ids = [a["id"] for a in acc_opts]
        acc_labels = {a["id"]: a["name"] for a in acc_opts}
        c_a, c_b = st.columns(2)
        with c_a:
            name = st.text_input(
                "Name",
                placeholder="e.g., My index fund",
                help="Your own label — no symbols required.",
            )
            ticker = st.text_input(
                "Ticker (optional)",
                placeholder="e.g., VTI",
                help="Lets dividend & detail sections link mock data.",
            ).strip()
            typ = st.selectbox(
                "Type",
                ["mutual_fund", "stock"],
                format_func=lambda x: display_type(x),
                help="Mutual fund = pooled fund; Stock = single company shares.",
            )
        with c_b:
            category = st.selectbox(
                "What best describes it?",
                [
                    "Equity / growth",
                    "Balanced / hybrid",
                    "Debt / stable",
                    "Single stock",
                ],
            )
            acct = st.selectbox(
                "Account",
                acc_ids,
                format_func=lambda i: acc_labels.get(i, i),
                help="Route this line to one of your investing accounts.",
            )
            value = st.number_input(
                "About how much is it worth today? ($)",
                min_value=0.0,
                value=1000.0,
                step=100.0,
                help="Total current value of this line (not the original deposit).",
            )
        if st.button("Save holding"):
            if name.strip():
                pr, prev = holding_mock_price_ticker(name.strip(), ticker or None)
                st.session_state.holdings.append(
                    {
                        "name": name.strip(),
                        "ticker": ticker.upper() if ticker else "",
                        "type": typ,
                        "category": category,
                        "value": float(value),
                        "account_id": acct,
                        "cost_basis_total": float(value) * 0.95,
                        "lots": [],
                        "mock_price": pr,
                        "mock_prev_close": prev,
                    }
                )
                st.success("Saved.")
                st.rerun()
            else:
                st.error("Please enter a name.")

    if st.session_state.holdings:
        ensure_portfolio_state(st.session_state)
        accmap = {a["id"]: a["name"] for a in st.session_state.accounts}
        rows = copy.deepcopy(st.session_state.holdings)
        for i, row in enumerate(rows):
            row["#"] = i + 1
            row["ticker"] = row.get("ticker") or "—"
            row["account_name"] = accmap.get(row.get("account_id"), "—")
        df = pd.DataFrame(rows)[
            ["#", "name", "ticker", "account_name", "type", "category", "value"]
        ]
        df["type"] = df["type"].map(display_type)
        df.rename(
            columns={
                "name": "Name",
                "ticker": "Ticker",
                "account_name": "Account",
                "type": "Type",
                "category": "What it’s like",
                "value": "About worth today ($)",
            },
            inplace=True,
        )
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.button("Clear all holdings", type="secondary"):
            st.session_state.holdings = []
            st.rerun()
    else:
        st.info("No holdings yet — add one above or load the sidebar example.")

# ----- Goals / onboarding -----
with tab_goals:
    st.subheader("Guided goal-setting")
    st.markdown(
        "We won't ask for Alphas, Betas, or Sharpe ratios. "
        "Just your **goal**, **timeline**, and **how market swings feel** — that shapes a sensible target mix."
    )

    with st.form("onboarding_form"):
        goal = st.radio(
            "What is the main reason you're investing?",
            [
                "Grow wealth over time",
                "Save for a big purchase (home, education)",
                "Build an emergency cushion while growing slowly",
                "Preserve what I have while beating inflation a little",
            ],
        )
        horizon = st.selectbox(
            "When will you likely need a large part of this money?",
            [
                "Less than 3 years",
                "3–5 years",
                "5–10 years",
                "More than 10 years",
            ],
        )
        comfort = st.radio(
            "If your portfolio dropped temporarily, which statement fits best?",
            [
                "I'd panic and want to sell — even a ~10% dip feels scary",
                "A moderate dip (around 15%) is stressful but okay",
                "I can ride out a serious dip (25–30%) if my goals haven't changed",
            ],
        )
        submitted = st.form_submit_button("Save my profile")
        if submitted:
            st.session_state.onboarding = {
                "goal": goal,
                "horizon": horizon,
                "comfort": comfort,
            }
            st.success("Profile saved. Check your Dashboard for updated targets.")

    if st.session_state.onboarding:
        p = profile_from_onboarding(st.session_state.onboarding)
        st.markdown("#### How we translate your answers")
        st.markdown(
            f"- **Summary:** {p.label}\n"
            f"- **Target mix:** about **{p.growth_target_pct:.0f}%** growth-style, "
            f"**{p.balanced_target_pct:.0f}%** balanced, **{p.stable_target_pct:.0f}%** stable.\n"
            "\n"
            "Targets are **starting points**, not predictions. They exist so you can compare "
            "your real holdings to a mix that matches your timeline and comfort — that's all."
        )

# ----- Scenarios -----
with tab_scenarios:
    st.subheader("What-if scenarios — ideas, not instructions")
    st.warning(
        "**Risks:** Investments can lose money. Past patterns don’t guarantee the future. "
        "This tool uses **simple teaching assumptions** so you can think clearly — it is **not** personalized advice."
    )
    st.caption(
        "Pick a situation. We turn it into **plain steps**, **rough dollar sizes**, and **why** — "
        "plus honest notes on **fees** and **taxes**."
    )

    scenario_labels = {s["id"]: s["title"] for s in SCENARIOS}
    choice = st.selectbox(
        "What are you thinking about?",
        list(scenario_labels.keys()),
        format_func=lambda k: scenario_labels[k],
        help="Each option is a different life or market story.",
    )
    shock_pct = st.slider(
        "Teaching assumption: if broad stock investments drop by (%)",
        min_value=5,
        max_value=45,
        value=20,
        help="Used only for the stress estimate below — you control the story.",
    )

    meta = next(s for s in SCENARIOS if s["id"] == choice)
    st.markdown(f"**In plain words:** {meta['blurb']}")

    rec = recommend_for_scenario(
        choice,
        st.session_state.holdings,
        profile,
        equity_shock_pct=float(shock_pct),
    )
    tot = portfolio_total(st.session_state.holdings)
    st_res = rec.get("stress") or {}

    if tot > 0 and st_res.get("total_before"):
        s1, s2, s3 = st.columns(3)
        with s1:
            st.metric(
                "Rough portfolio change in this stress test",
                f"{st_res['pct_change']:.1f}%",
                help="Uses simple bucket sensitivities — not a forecast.",
            )
        with s2:
            st.metric(
                "About $ change",
                f"${st_res['dollar_change']:,.0f}",
                help="Illustrative only.",
            )
        with s3:
            st.metric(
                "Assumed stock-market drop",
                f"{st_res.get('assumed_equity_drop_pct', shock_pct):.0f}%",
            )

    st.markdown("#### Suggested direction")
    for a in rec["actions"]:
        st.markdown(f"- {a}")
    if rec.get("dollar_hint"):
        st.info(rec["dollar_hint"])

    st.markdown("#### Why we suggest this")
    for r in rec["rationale"]:
        st.markdown(f"- {r}")

    with st.expander("How this math works (transparency)", expanded=False):
        sens_lines = [
            f"- **{BUCKET_LABELS[k]}:** in this story, each dollar here loses about **{shock_pct * v:.1f}%** "
            f"(we multiply the **{shock_pct}%** story by sensitivity **×{v:.2f}**)."
            for k, v in BUCKET_MARKET_SENSITIVITY.items()
        ]
        st.markdown(
            "### Stress test\n"
            f"We assume broad equities drop **{shock_pct}%**. Each slice of your portfolio moves a fraction of that "
            f"({', '.join(BUCKET_MARKET_SENSITIVITY.keys())} sensitivities). "
            "That yields the dollar and percent change above.\n\n"
            + "\n".join(sens_lines)
        )
        if rec.get("shift_pp"):
            st.markdown(
                f"### Rebalance hint\n"
                f"We translated the scenario into about **{rec['shift_pp']:.1f} percentage points** of your **total** "
                f"portfolio to shift between styles when applicable — then converted to dollars using your entered total."
            )
        st.caption(
            "Sensitivities are fixed for transparency in a classroom prototype; a live product might let you tune them."
        )

    with st.expander("Transparency: costs & taxes", expanded=True):
        st.markdown(
            f"**Costs:** {rec['costs_note']}\n\n**Taxes:** {rec['tax_note']}\n\n"
            f"_Your profile used for context:_ {rec['profile_label']}"
        )

# ----- Research / Cortex-style (spec — simulated) -----
with tab_research:
    render_cortex_research_tab()

# ----- Robinhood Gold tier (spec 1.4 — simulated) -----
with tab_gold:
    render_gold_tab()

# ----- Banking & financial services (spec 1.6 — simulated) -----
with tab_banking:
    render_banking_tab()

# ----- Robinhood Legend — advanced platform (spec 1.5 — simulated) -----
with tab_legend:
    render_legend_tab()

# ----- Simulated trading desk (spec 1.1 style) -----
with tab_trade:
    render_trading_sim_tab(portfolio_total(st.session_state.holdings))

# ----- Social & gamification (spec 1.7 — simulated) -----
with tab_social:
    render_social_tab()

# ----- Optional layered features (does not modify core tab bodies above) -----
with tab_addons:
    render_custom_features_tab()

st.divider()
st.caption(
    "Educational prototype — not investment, tax, or legal advice. "
    "Verify fees and taxes with your broker and local rules before acting."
)
