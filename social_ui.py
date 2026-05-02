"""
§1.7 Social, community & gamification — simulation UI.
"""

from __future__ import annotations

import uuid

import pandas as pd
import streamlit as st

from portfolio_logic import allocation_pcts, portfolio_total
from social_sim import (
    LAUNCH_STORY,
    MOCK_TRADERS,
    discussion_teasers,
    free_stock_value_band,
    live_trade_feed,
    referral_reward_story,
    tipranks_style_tables,
)


def render_social_tab() -> None:
    ss = st.session_state
    ss.setdefault("social_following", [])
    ss.setdefault("referral_code", f"RH-{uuid.uuid4().hex[:6].upper()}")
    ss.setdefault("referrals_log", [])
    ss.setdefault("share_show_dollars", False)

    st.subheader("Social & community (simulated)")
    st.caption(LAUNCH_STORY + " — **no real network**; feeds are fabric for class demos.")

    # ----- Social hub -----
    st.markdown("#### Robinhood Social (mobile-first story)")
    st.info(
        "**Follow** traders, **live trades** feed, **ideas & strategy threads**, **public P&L profiles** — "
        "this web tab mirrors the feature list only."
    )

    follow_opts = [t["handle"] for t in MOCK_TRADERS]
    ss.social_following = st.multiselect(
        "Follow (sim)",
        follow_opts,
        default=[x for x in ss.social_following if x in follow_opts],
        help="Updates your personalized feed below.",
    )

    st.markdown("**Public P&L profiles (mock)**")
    st.dataframe(pd.DataFrame(MOCK_TRADERS), use_container_width=True, hide_index=True)

    st.markdown("**Live trades — sample feed**")
    st.dataframe(pd.DataFrame(live_trade_feed(seed=hash(tuple(ss.social_following)) % 10000)), use_container_width=True, hide_index=True)

    st.markdown("**Discussion teasers**")
    for t in discussion_teasers():
        st.markdown(f"- {t}")

    st.markdown("**Visibility: politicians · hedge funds · insiders (TipRanks-style sim)**")
    pol, hf, ins = tipranks_style_tables()
    t1, t2, t3 = st.tabs(["Politicians", "Hedge funds", "Insiders"])
    with t1:
        st.dataframe(pol, use_container_width=True, hide_index=True)
    with t2:
        st.dataframe(hf, use_container_width=True, hide_index=True)
    with t3:
        st.dataframe(ins, use_container_width=True, hide_index=True)
    st.caption("Rows are **placeholders** — real TipRanks-style feeds are licensed & delayed.")

    st.divider()

    # ----- Portfolio sharing -----
    st.markdown("#### Portfolio sharing card")
    total = portfolio_total(ss.holdings)
    pcts = allocation_pcts(ss.holdings) if ss.holdings else {"growth": 0, "balanced": 0, "stable": 0}
    top_lines = sorted(ss.holdings, key=lambda h: float(h.get("value", 0) or 0), reverse=True)[:3]
    ss.share_show_dollars = st.checkbox(
        "Show dollar amounts on card (default: **hidden**)",
        value=bool(ss.share_show_dollars),
    )
    demo_ytd = 7.4 + (hash(str(ss.holdings)) % 20) / 10.0 - 1.0  # stable-ish fake YTD for card
    card_md = "### My portfolio snapshot *(sim)*\n"
    card_md += f"- **Illustrative YTD return:** ~**{demo_ytd:.1f}%** (mock — not live)\n"
    if not ss.share_show_dollars:
        card_md += "- **Values:** hidden\n"
    else:
        card_md += f"- **Total (entered):** ${total:,.0f}\n"
    card_md += f"- **Mix:** growth **{pcts['growth']:.0f}%** · balanced **{pcts['balanced']:.0f}%** · stable **{pcts['stable']:.0f}%**\n"
    card_md += "- **Top sleeves:**\n"
    for h in top_lines:
        nm = h.get("name", "")
        w = 100.0 * float(h.get("value", 0) or 0) / total if total else 0
        if ss.share_show_dollars:
            card_md += f"  - {nm} · **${float(h.get('value', 0)):,.0f}** (~{w:.0f}%)\n"
        else:
            card_md += f"  - {nm} · ~**{w:.0f}%** of portfolio\n"
    card_md += "\n*Educational prototype — not performance marketing.*\n"
    st.markdown(card_md)
    share_url = f"https://example.invalid/share/{ss.referral_code}"
    st.code(share_url, language=None)
    st.caption("**Direct link + social share** would open OS sheet on mobile; here we show a fake URL.")

    st.divider()

    # ----- Referrals -----
    st.markdown("#### Referral program (sim)")
    story = referral_reward_story()
    st.markdown(f"- **Referrer:** {story['referrer']}")
    st.markdown(f"- **Friend:** {story['referee']}")
    st.caption(story["fine_print"])
    lo, hi = free_stock_value_band()
    st.metric("Illustrative free-stock band", f"${lo:.0f} – ${hi:.0f} notional")

    st.text_input("Your referral code (session)", value=ss.referral_code, disabled=True)
    friend_email = st.text_input("Simulate friend funded account (label)", placeholder="friend@example.com")
    if st.button("Record referral + grant mock stock"):
        if friend_email.strip():
            ss.referrals_log.append(
                {
                    "friend": friend_email.strip(),
                    "status": "Funded (sim)",
                    "reward_notional": f"${lo:.0f}-${hi:.0f} slice",
                }
            )
            st.success("Logged — both sides get a **mock** free-stock credit in this prototype.")
        else:
            st.warning("Enter a label to simulate.")

    if ss.referrals_log:
        st.dataframe(pd.DataFrame(ss.referrals_log), use_container_width=True, hide_index=True)
