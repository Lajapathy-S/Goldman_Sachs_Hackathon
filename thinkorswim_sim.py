"""
thinkorswim platforms — Desktop / Web / Mobile / studies / thinkScript (story-level simulation).
"""

from __future__ import annotations

import math
import random
from typing import Any

TECHNICAL_STUDIES_COUNT_STORY = 400
MOBILE_APP_STORE_RATING_STORY = 4.7
MOBILE_CHART_STUDIES_STORY = 300


def thinkorswim_desktop_story() -> dict[str, Any]:
    return {
        "product": "thinkorswim Desktop (flagship)",
        "delivery": "Fully downloadable Windows / macOS installer",
        "pricing": "No separate charge — included with Schwab brokerage accounts (story)",
        "customization": "Workspaces, gadgets, linked windows, flex grids — deeply customizable layout",
        "asset_classes": ["Stocks", "ETFs", "Options", "Futures", "Forex"],
        "positioning": "Widely cited as an advanced active-trader benchmark — simulation copy only.",
    }


def thinkorswim_web_story() -> dict[str, Any]:
    return {
        "product": "thinkorswim Web",
        "delivery": "Browser-based — **no download**",
        "core_features": [
            "Streaming quotes",
            "Charting",
            "Options chain",
            "Order entry / ticket",
        ],
        "purpose": "Users who want core thinkorswim capabilities without installing desktop software (story).",
    }


def thinkorswim_mobile_story() -> dict[str, Any]:
    return {
        "product": "thinkorswim Mobile",
        "charting": f"Advanced charts with **{MOBILE_CHART_STUDIES_STORY}+** technical studies (story)",
        "options": "Multi-leg option orders from mobile ticket",
        "voice": "Voice commands for quote lookup and trade placement where enabled — see **Voice Command Trading** below.",
        "app_store_rating_story": MOBILE_APP_STORE_RATING_STORY,
        "note": "Ratings change over time — figure is from spec sheet narrative.",
    }


def voice_command_trading_mobile_story() -> dict[str, Any]:
    return {
        "feature": "Voice Command Trading (Mobile)",
        "platform": "thinkorswim **Mobile** only (story)",
        "hands_free": "Hands-free quotes, charts, and guided trade flows where microphone permissions allow",
        "example_phrases": [
            "Get quote for Apple",
            "Show me the SPY chart",
            "Place a buy order for 10 shares of Tesla",
        ],
        "safety_flow": "Orders typically confirm symbol, side, quantity, and order type before submit — voice is an input layer, not blind execution (story).",
        "availability": "Dependent on device OS speech recognition & firm risk controls — phrasing may vary by locale.",
    }


def schwab_coaching_education_story() -> dict[str, Any]:
    return {
        "program": "Schwab Coaching® Education (In-Platform)",
        "surface": "Integrated **education** entry inside thinkorswim — tab / panel that stays in context (story)",
        "behavior": (
            "Links directly to **relevant tutorial videos and articles** based on the **tool or strategy** "
            "the user is currently using — e.g. opening Analyze opens options-Greek explainers; chart studies link to study docs."
        ),
        "examples": [
            "From **Options chain** → vertical spread walkthroughs",
            "From **thinkScript editor** → syntax & sample library articles",
            "From **Analyze → Probability Analysis** → POP / expected move primers",
        ],
        "note": "Content catalog and personalization rules are illustrative — not live LMS data.",
    }


def technical_studies_library_story() -> dict[str, Any]:
    categories = {
        "Trend / smoothing": ["Simple / exponential MAs", "MACD", "ADX"],
        "Momentum": ["RSI", "Stochastic", "Williams %R"],
        "Volatility": ["Bollinger Bands", "Keltner Channels", "Historical volatility"],
        "Volume / auction": ["Volume Profile", "VWAP", "OnBalanceVolume"],
        "Japanese / specialty": ["Ichimoku", "Renko", "Heikin Ashi"],
        "Drawing / ratios": ["Fibonacci retracements/extensions", "Anchored VWAP"],
        "thinkorswim-only flavors": ["Monkey Bars® profile views", "Flexible chart styles"],
    }
    return {
        "catalog_size_story": f"{TECHNICAL_STUDIES_COUNT_STORY}+ technical studies & indicators",
        "categories": categories,
        "scripted_extensions": "Many studies exposed via thinkScript™ — see community scripts.",
    }


CHART_LAYOUTS_MAX_SAVE_STORY = 20
STRATEGY_BUILDER_ETA_STORY = "2026"


def papermoney_story() -> dict[str, Any]:
    return {
        "product": "paperMoney® Virtual Trading",
        "summary": (
            "Full paper-trading simulation using **live market data** — test strategies, practice options, "
            "validate indicators **without** risking real money (story)."
        ),
        "data": "Streams live quotes for simulation — paper balances only",
        "use_cases": [
            "Test strategies end-to-end",
            "Practice options & multi-leg tickets",
            "Validate studies / thinkScript before live",
        ],
        "platforms": "Available on **all three** thinkorswim platforms — Desktop, Web, Mobile (story)",
    }


def charts_navigator_story() -> dict[str, Any]:
    return {
        "feature": "Charts Navigator",
        "scope": "thinkorswim **Desktop** only (story)",
        "behavior": (
            "Bird's-eye overview of **full price history** alongside a **zoomed-in** chart — "
            "**chart context stays visible** regardless of zoom level."
        ),
    }


def multichart_my_tools_story() -> dict[str, Any]:
    return {
        "feature": "Multi-Chart Navigation — My Tools",
        "scope": "Desktop only (story)",
        "layouts": f"Up to **{CHART_LAYOUTS_MAX_SAVE_STORY}** chart layouts saveable",
        "workflow": (
            "Quickly switch between **saved chart configurations** for **multiple time frames** "
            "via the **My Tools** panel (story)."
        ),
    }


def trade_flash_story() -> dict[str, Any]:
    return {
        "gadget": "Trade Flash (Real-Time Event Alerts)",
        "feed_style": "Real-time gadget — headlines as events occur (story)",
        "events": [
            "Third-party analyst upgrades / downgrades",
            "Block trades",
            "Trade imbalances",
            "Trading floor / venue events",
            "Earnings surprises",
        ],
        "note": "Third-party data subject to exchange licensing — latency varies by venue (story).",
    }


def mock_trade_flash_rows(n: int = 7, seed: int = 91) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    kinds = ["Upgrade", "Block trade", "Imbalance", "Floor note", "EPS surprise"]
    rows = []
    for i in range(n):
        rows.append(
            {
                "Time (sim)": f"{9 + i // 4}:{30 + (i % 4) * 10:02d} ET",
                "Symbol": rng.choice(["AAPL", "NVDA", "XOM", "SPY", "QQQ"]),
                "Headline (sim)": rng.choice(kinds) + f" — headline #{i+1}",
            }
        )
    return rows


def oco_alerts_story() -> dict[str, Any]:
    return {
        "feature": "One-Cancels-Other (OCO) Alerts",
        "scope": "thinkorswim **Desktop** only (story)",
        "behavior": (
            "Set **two** simultaneous price alerts — when **one fires**, the other is **automatically cancelled**."
        ),
        "use_cases": [
            "Track **breakouts** or **pullbacks** with **competing** price levels without duplicate fills on alerts",
        ],
    }


def walk_limit_options_platforms_story() -> dict[str, Any]:
    return {
        "order_type": "Walk Limit® Orders (Options)",
        "behavior": (
            "Proprietary order type — **incrementally adjusts** the limit price to improve fill likelihood "
            "**without** aggressively chasing / crossing the spread (story)."
        ),
        "availability": "Available on **all three** thinkorswim platforms — Desktop, Web, Mobile (story)",
    }


def options_backtesting_story() -> dict[str, Any]:
    return {
        "capability": "Options Back-Testing",
        "summary": (
            "Historical analysis of options strategies vs **past market data** — hypothetical returns "
            "across **defined time windows** (story)."
        ),
        "method": "Replay historical chains — hypothetical fills vs underlying path",
        "outputs": ["P/L envelope by date", "Assignment stats where relevant", "Sensitivity vs realized vol"],
        "caution": "Past paths ≠ future — liquidity & assignment assumed away in sim math (story).",
    }


def volatility_probability_story() -> dict[str, Any]:
    return {
        "suite": "Volatility & Probability Analysis",
        "tools": [
            "Probability of profit (POP)",
            "Probability of touching a strike / zone",
            "Expected move (from ATM implied vol)",
            "Implied volatility surface & skew snapshots",
            "IV percentile vs trailing realized",
            "Term structure — IV vs expiration",
        ],
        "delivery": "Analyze tab / theoretical pricing gadgets on desktop; subsets on web/mobile (story).",
    }


def economic_data_gadget_story() -> dict[str, Any]:
    return {
        "gadget": "Economic Data Indicator Database",
        "overlay": (
            "Historical economic series (e.g. CPI, NFP, GDP, Fed Funds) **overlaid on charts** "
            "via the Economic Data gadget — macro-driven workflows (story)."
        ),
        "series_examples": [
            "CPI / Core CPI",
            "Nonfarm payrolls (NFP)",
            "GDP prints",
            "Effective Fed Funds rate",
            "Retail sales / PMI (where wired)",
        ],
        "use_case": "Anchor discretionary trades to macro release timing — still watch gaps/slippage (story).",
    }


def black_scholes_call(
    S: float,
    K: float,
    T_years: float,
    r: float,
    sigma: float,
) -> tuple[float, dict[str, float]]:
    """Naive Black-Scholes call + common Greeks for educational UI."""
    if T_years <= 0 or sigma <= 0 or S <= 0:
        intrinsic = max(0.0, S - K)
        return intrinsic, {"delta": 1.0 if S > K else 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}

    sqt = sigma * math.sqrt(T_years)
    d1 = (math.log(S / K) + (r + 0.5 * sigma * sigma) * T_years) / sqt
    d2 = d1 - sqt

    def _ncdf(x: float) -> float:
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))

    nd1 = _ncdf(d1)
    nd2 = _ncdf(d2)
    price = S * nd1 - K * math.exp(-r * T_years) * nd2

    pdf_d1 = math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi)
    delta = nd1
    gamma = pdf_d1 / (S * sqt)
    vega = S * pdf_d1 * math.sqrt(T_years) / 100.0
    theta = (
        -S * pdf_d1 * sigma / (2 * math.sqrt(T_years))
        - r * K * math.exp(-r * T_years) * _ncdf(d2)
    ) / 365.0

    return price, {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta}


def what_if_option_scenario(
    spot: float,
    strike: float,
    d_spot: float,
    t_years: float,
    d_t_days: float,
    iv: float,
    d_iv: float,
    rate: float = 0.045,
) -> dict[str, Any]:
    """Per-contract P/L from repricing after spot/time/IV shocks (teaching stub)."""
    p0, g0 = black_scholes_call(spot, strike, t_years, rate, iv)
    spot1 = max(0.01, spot + d_spot)
    t1 = max(1e-6, t_years + d_t_days / 365.0)
    iv1 = max(0.01, iv + d_iv)
    p1, _ = black_scholes_call(spot1, strike, t1, rate, iv1)
    return {
        "feature": "What-If Scenario Analysis",
        "model": "Black-Scholes European call (teaching stub — powered by BS-style repricing)",
        "intent": "Hypothetical trade — vary spot, time to expiration, IV and view estimated option value / P&L impact (story)",
        "price_before": round(p0, 4),
        "price_after_shock": round(p1, 4),
        "pnl_per_contract_shares": round((p1 - p0) * 100, 2),
        "greeks_at_start": {k: round(v, 6) for k, v in g0.items()},
        "shocks": {
            "d_spot": d_spot,
            "d_t_days": d_t_days,
            "d_iv": d_iv,
        },
    }


def automated_strategy_builder_story() -> dict[str, Any]:
    return {
        "product": "Automated Strategy Builder (AI-Assisted, in development)",
        "status": "AI-assisted tooling — **in development**",
        "eta_story": f"Announced for **{STRATEGY_BUILDER_ETA_STORY}** (story)",
        "flow": (
            "Describe a trading strategy in **plain language** → receive a drafted **thinkScript™** implementation "
            "for editing, back-testing, and paperMoney validation (story)."
        ),
        "guardrails": "Back-test & paper trade before live capital — AI output is not a recommendation.",
    }


def thinkscript_story() -> dict[str, Any]:
    snippet = '''# Example: plot a fast/slow MA crossover flag (thinkScript™ story syntax — not executed here)
input fastLength = 9;
input slowLength = 21;
def fastAvg = Average(close, fastLength);
def slowAvg = Average(close, slowLength);
plot bullishCross = fastAvg crosses above slowAvg;
'''
    return {
        "language": "thinkScript™ — Schwab / TD Ameritrade proprietary scripting",
        "capabilities": [
            "Custom **studies** (plots on chart)",
            "Custom **strategies** with simulated backtests on desktop (story)",
            "Alerts conditioned on script logic",
        ],
        "community": "Large shared library of user-contributed scripts — vet before relying on them.",
        "ai_assist": "AI-assisted scripting tools — in development / phased rollout (story).",
        "sample_snippet": snippet.strip(),
    }
