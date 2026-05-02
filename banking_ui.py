"""
§1.6 Banking, payments & financial services — simulation UI.
"""

from __future__ import annotations

import streamlit as st

from banking_sim import (
    BANKING_LAUNCH_YEAR,
    CASH_DELIVERY_MARKETS,
    FDIC_PASS_THROUGH_MAX_USD,
    GOLD_CARD_CASHBACK_RATE,
    IRA_TYPES,
    SAVINGS_APY_GOLD_BANKING,
    estate_tax_services_blurb,
    family_accounts_blurb,
    gold_banking_savings_yield,
    gold_card_cashback_yearly,
    ira_room_remaining,
    private_markets_rvi_factsheet,
)


def render_banking_tab() -> None:
    ss = st.session_state
    ss.setdefault("gold_banking_unlocked", False)
    ss.setdefault("gold_card_reinvest", True)
    ss.setdefault("family_members", [])
    ss.setdefault("ira_ytd_traditional", 0.0)
    ss.setdefault("ira_ytd_roth", 0.0)
    ss.setdefault("savings_balance_demo", 15000.0)

    st.subheader("Banking & financial services (simulated)")
    st.warning(
        "**Not a bank or broker-dealer.** Copy describes Robinhood-style products for your prototype; "
        "no accounts, cards, or wires exist here."
    )

    gold_member = bool(ss.get("rh_gold_subscribed"))
    st.markdown(
        f"**Gold subscription (sim):** {'active' if gold_member else 'off'} — "
        "many banking perks are framed as **Gold + Banking** in the spec."
    )

    ss.gold_banking_unlocked = st.checkbox(
        "Enable **Gold Banking** story (checking + savings suite)",
        value=bool(ss.gold_banking_unlocked),
        disabled=not gold_member,
        help="Spec: Gold-exclusive full banking. Toggle Gold on the Gold tab first.",
    )

    if gold_member and ss.gold_banking_unlocked:
        st.success(
            f"**Robinhood Banking** (story): launched **{BANKING_LAUNCH_YEAR}** · checking & savings · "
            f"**debit**, **direct deposit**, **bill pay** · FDIC pass-through up to **${FDIC_PASS_THROUGH_MAX_USD/1e6:.2f}M** via partner banks."
        )
        ss.savings_balance_demo = float(
            st.number_input(
                "Savings balance for demo ($)",
                min_value=0.0,
                value=float(ss.savings_balance_demo),
                step=500.0,
                key="bank_save_bal",
            )
        )
        snap = gold_banking_savings_yield(ss.savings_balance_demo)
        st.metric(
            f"Savings ({SAVINGS_APY_GOLD_BANKING * 100:.0f}% APY story)",
            snap.est_annual_interest,
        )
        st.caption("Rate **variable**; partner-bank sweep disclosures apply in real life.")

    elif gold_member and not ss.gold_banking_unlocked:
        st.info("Turn on **Gold Banking** above to show checking/savings tools.")

    else:
        st.info("Subscribe on **Gold (sim)** to unlock the Gold Banking checklist.")

    st.divider()

    st.markdown("#### Robinhood Gold Card (credit)")
    spend = st.number_input("Illustrative annual card spend ($)", min_value=0.0, value=24000.0, step=1000.0)
    cb = gold_card_cashback_yearly(spend)
    st.metric(
        f"{GOLD_CARD_CASHBACK_RATE * 100:.0f}% back on all categories (story)",
        f"${cb['cash_back_usd']:,.2f}/yr est.",
        f"${cb['annual_fee']:.0f} annual fee",
    )
    st.caption(cb["issuer_story"])
    ss.gold_card_reinvest = st.toggle(
        "Sweep cash back to **brokerage** (vs hold as cash)",
        value=bool(ss.gold_card_reinvest),
    )
    st.caption(cb["reinvest_story"])

    st.markdown("#### Cash delivery (banking perk)")
    st.markdown(
        "**Premium perk (story):** physical **cash to your door** in **select markets** — prototype lists cities only."
    )
    st.multiselect("Eligible markets (illustrative)", list(CASH_DELIVERY_MARKETS), default=[])

    with st.expander("Estate planning & tax advice (Gold Banking)"):
        st.markdown(estate_tax_services_blurb())

    with st.expander("Family accounts"):
        st.markdown(family_accounts_blurb())
        nm = st.text_input("Add family member display name (sim)")
        if st.button("Add to household list") and nm.strip():
            ss.family_members = list(ss.family_members) + [nm.strip()]
        if ss.family_members:
            st.write("Household (sim): **" + "**, **".join(ss.family_members) + "**")

    st.markdown("#### Private markets — Ventures Fund I (RVI story)")
    fs = private_markets_rvi_factsheet()
    for k, v in fs.items():
        st.markdown(f"- **{k}:** {v}")

    st.markdown("#### IRA account management (sim)")
    ira_type = st.selectbox("IRA type", IRA_TYPES)
    if ira_type == "Roth IRA":
        ss.ira_ytd_roth = float(
            st.number_input(
                "YTD contributions — Roth ($)",
                min_value=0.0,
                value=float(ss.ira_ytd_roth),
                step=100.0,
                key="ira_r",
            )
        )
        room = ira_room_remaining(ss.ira_ytd_roth)
    else:
        label = "YTD contributions — Traditional / rollover ($)"
        ss.ira_ytd_traditional = float(
            st.number_input(
                label,
                min_value=0.0,
                value=float(ss.ira_ytd_traditional),
                step=100.0,
                key="ira_t",
            )
        )
        room = ira_room_remaining(ss.ira_ytd_traditional)

    st.metric("Remaining room (illustrative limit)", f"${room['remaining']:,.2f}")
    lim = room["limit"]
    st.caption(
        "Tax-year designation & automated investing inside IRA would live here; **SIPC** covers brokerage assets "
        "(not cash in bank — **FDIC** for banking story above). "
        f"Illustrative annual contribution cap **${lim:,.0f}**."
    )
