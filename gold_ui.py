"""
Robinhood Gold tier — simulated subscription UX & calculators (§1.4).
"""

from __future__ import annotations

from datetime import date, timedelta

import streamlit as st

from gold_sim import (
    APY_NON_GOLD_CASH,
    APY_GOLD_CASH,
    MIN_ACCOUNT_FOR_MARGIN,
    MARGIN_RATE_ILLUSTRATIVE,
    SUBSCRIPTION_USD_PER_MONTH,
    TRIAL_DAYS,
    ira_contribution_match_gold,
    managed_portfolio_fee_gold,
    margin_eligibility,
    margin_interest_illustrative,
    rollover_transfer_match,
    uninvested_cash_yield,
)
from portfolio_logic import portfolio_total
from trading_sim import instant_deposit_limits


def render_gold_tab() -> None:
    ss = st.session_state
    ss.setdefault("rh_gold_subscribed", False)
    ss.setdefault("rh_gold_trial_started", None)

    invested = portfolio_total(ss.holdings)
    cash = float(ss.get("cash_balance_usd") or 0.0)
    account_total = invested + cash

    st.subheader("Robinhood Gold — premium tier (simulated)")
    st.caption(
        f"**${SUBSCRIPTION_USD_PER_MONTH:.0f}/month** after trial · illustrative calculators · "
        "**not** tax, retirement, or lending advice."
    )

    c_sub1, c_sub2 = st.columns(2)
    with c_sub1:
        sub = st.checkbox(
            "I subscribe (simulation)",
            value=bool(ss.rh_gold_subscribed),
            help="Turns on Gold-tier rates in calculators below; manage billing is not implemented.",
        )
        ss.rh_gold_subscribed = sub
        if sub:
            if ss.rh_gold_trial_started is None:
                ss.rh_gold_trial_started = date.today().isoformat()
            trial_end = date.fromisoformat(ss.rh_gold_trial_started) + timedelta(days=TRIAL_DAYS)
            days_left = (trial_end - date.today()).days
            st.success(
                f"**First {TRIAL_DAYS} days free** (sim): trial ends **{trial_end.isoformat()}** "
                f"({max(0, days_left)} days remaining in story)."
            )
        else:
            st.info("Subscribe to unlock **Gold** rates in the calculators (still safe demo data).")

    with c_sub2:
        if st.button("Sync Research tab → Gold = subscribed"):
            ss.cortex_gold = bool(ss.rh_gold_subscribed)
            st.success("**Research & AI** Gold toggle aligned.")
        st.caption("Cortex AI and higher instant deposits are framed as **Gold** in this prototype.")

    gold_active = bool(ss.rh_gold_subscribed)

    st.divider()
    st.markdown("#### 3% IRA contribution match")
    ira_in = st.number_input(
        "Annual IRA contribution you plan ($)",
        min_value=0.0,
        value=7500.0,
        step=100.0,
        key="gold_ira_contrib",
        help="Illustrative — real IRS limits apply.",
    )
    ir = ira_contribution_match_gold(ira_in)
    st.metric("Estimated match (capped)", f"${ir.capped_match:,.2f}", f"raw 3% = ${ir.raw_match:,.2f}")
    st.caption(ir.note)

    st.markdown("#### 1% IRA / 401(k) rollover match")
    roll = st.number_input("Rollover amount transferred in ($)", min_value=0.0, value=50000.0, step=1000.0, key="gold_roll")
    rm = rollover_transfer_match(roll)
    st.metric("Unlimited 1% match (sim)", f"${rm['match_usd']:,.2f}")
    st.caption(rm["note"])

    st.markdown("#### Cash APY on uninvested brokerage cash")
    yld_g = uninvested_cash_yield(cash, True)
    yld_ng = uninvested_cash_yield(cash, False)
    g1, g2 = st.columns(2)
    with g1:
        st.metric(
            f"Gold ({APY_GOLD_CASH * 100:.2f}% APY story)",
            f"~${yld_g['estimated_annual_interest']:,.2f}/yr",
            help="FDIC sweep framing from spec.",
        )
    with g2:
        st.metric(
            f"Non-Gold ({APY_NON_GOLD_CASH * 100:.2f}% APY story)",
            f"~${yld_ng['estimated_annual_interest']:,.2f}/yr",
        )
    st.caption(
        f"Uses **cash** from Dashboard net-worth inputs (**${cash:,.0f}**). "
        "Gold toggle above selects which column applies to you."
        if gold_active
        else "Subscribe (sim) to treat yourself as Gold for the left column."
    )

    st.markdown("#### Margin — first $1,000 interest-free (Gold story)")
    mel = margin_eligibility(account_total)
    st.caption(
        f"Account value (investments + cash): **${account_total:,.0f}**. "
        f"Minimum **${MIN_ACCOUNT_FOR_MARGIN:,.0f}** for margin (sim rule): "
        f"**{'yes' if mel['meets_minimum_for_margin'] else 'no'}**."
    )
    bor = st.number_input("Borrowed on margin ($)", min_value=0.0, value=2500.0, step=100.0, key="gold_margin_borrow")
    mi = margin_interest_illustrative(bor)
    st.metric("Estimated annual margin interest (after free slice)", f"${mi['estimated_annual_interest']:,.2f}")
    st.caption(mi["note"] + f" Extra balance charged at **~{MARGIN_RATE_ILLUSTRATIVE:.1%}** in this demo.")

    st.markdown("#### Larger instant deposits (Gold)")
    lim = instant_deposit_limits(invested)
    st.metric("Standard instant ACH ceiling (story)", f"${lim['standard_instant_ach_usd']:,.0f}")
    st.metric("Gold-style ceiling (min $5k vs 3× portfolio)", f"${lim['illustrative_tier_ceiling_usd']:,.0f}")
    st.caption("Uses **portfolio investments** total as portfolio value proxy — same helper as Trading tab.")

    st.markdown("#### Robinhood Strategies (managed portfolios)")
    aum = st.number_input("Assets in Strategies ($)", min_value=0.0, value=75000.0, step=5000.0, key="gold_strat_aum")
    fee = managed_portfolio_fee_gold(aum)
    st.metric("Estimated annual management fee", f"${fee['estimated_annual_fee_usd']:,.2f}")
    st.info(fee["tier_description"])
    st.caption(fee["note"])

    with st.expander("Holdings rationale (placeholder)"):
        st.markdown(
            "Production Gold surfaces **why each ETF** is held and team commentary. "
            "Here: imagine a diversified sleeve map aligned to your risk answers on **Goals & profile**."
        )
