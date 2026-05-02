"""
Fidelity Trader+ — educational mocks; not Fidelity software or data.
"""

from __future__ import annotations

import math
import random
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

LAUNCH_STORY = "Fidelity **Trader+** — Sept **2025** (story), unified advanced platform (replaces **Active Trader Pro** narrative)."

CHART_TIMEFRAMES = [
    "1 min",
    "5 min",
    "15 min",
    "1 hour",
    "1 day",
    "1 week",
    "1 month",
]
CHART_STYLES = ["Candlestick", "Bar (OHLC)", "Line (close)", "Heikin-Ashi"]

INDICATOR_COUNT_STORY = 100  # "100+"

CRYPTO_TRADER_PLUS = ["BTC", "ETH", "SOL", "LTC", "LINK", "AVAX", "XRP", "DOGE"]


def mock_streaming_quote(symbol: str, seed: int | None = None) -> dict[str, Any]:
    sym = (symbol or "SPY").upper()
    r = random.Random(seed if seed is not None else hash(sym) % (2**32))
    last = 400 + r.random() * 60
    spread = 0.01 + r.random() * 0.03
    bid = last - spread / 2
    ask = last + spread / 2
    return {
        "symbol": sym,
        "last": round(last, 2),
        "bid": round(bid, 2),
        "ask": round(ask, 2),
        "size_bid": r.randint(100, 5000),
        "size_ask": r.randint(100, 5000),
        "ts": datetime.now().strftime("%H:%M:%S"),
        "data_level": "Level 1 (simulated stream)",
    }


def ohlc_for_timeframe(timeframe: str, bars: int = 100, seed: int = 1) -> pd.DataFrame:
    """Vary bar count & noise by timeframe label for demo."""
    tf = (timeframe or "1 day").lower()
    rng = np.random.default_rng(seed)
    if "min" in tf:
        n = min(bars, 200)
        noise = 0.0015
        freq = "min"
    elif "hour" in tf:
        n = min(bars, 120)
        noise = 0.004
        freq = "h"
    elif "week" in tf:
        n = min(bars, 80)
        noise = 0.02
        freq = "W"
    elif "month" in tf:
        n = min(bars, 60)
        noise = 0.035
        freq = "MS"
    else:
        n = min(bars, 150)
        noise = 0.012
        freq = "D"
    ret = rng.standard_normal(n) * noise
    close = 100 * np.cumprod(1 + ret)
    open_ = np.roll(close, 1)
    open_[0] = close[0]
    high = np.maximum(open_, close) * (1 + rng.random(n) * 0.003)
    low = np.minimum(open_, close) * (1 - rng.random(n) * 0.003)
    idx = pd.date_range(end=datetime.now(), periods=n, freq=freq)[:n]
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=idx)


def heikin_ashi(df: pd.DataFrame) -> pd.DataFrame:
    h_close = (df["open"] + df["high"] + df["low"] + df["close"]) / 4.0
    h_open = pd.Series(index=df.index, dtype=float)
    h_open.iloc[0] = (df["open"].iloc[0] + df["close"].iloc[0]) / 2
    for i in range(1, len(df)):
        h_open.iloc[i] = (h_open.iloc[i - 1] + h_close.iloc[i - 1]) / 2
    h_high = pd.concat([df["high"], h_open, h_close], axis=1).max(axis=1)
    h_low = pd.concat([df["low"], h_open, h_close], axis=1).min(axis=1)
    return pd.DataFrame({"open": h_open, "high": h_high, "low": h_low, "close": h_close}, index=df.index)


def long_call_analytics(
    strike: float,
    premium_per_share: float,
    contracts: int = 1,
    multiplier: float = 100.0,
) -> dict[str, Any]:
    """Breakeven & max loss for long call; max profit narrative."""
    breakeven = strike + premium_per_share
    max_loss = -premium_per_share * multiplier * contracts
    return {
        "breakeven": round(breakeven, 2),
        "max_loss_usd": round(max_loss, 2),
        "max_gain": "Unlimited (calls) — teaching label",
        "multiplier": multiplier,
        "contracts": contracts,
    }


def rough_itm_probability(
    spot: float,
    strike: float,
    days: float,
    iv: float,
) -> float:
    """Very rough Black–Scholes–style log-moneyness toy (not for trading)."""
    if spot <= 0 or strike <= 0 or days <= 0:
        return 0.0
    t = max(days / 365.0, 1e-6)
    vol = max(iv, 1e-6)
    d2 = (math.log(spot / strike) - 0.5 * vol * vol * t) / (vol * math.sqrt(t))
    return max(0.0, min(1.0, 0.5 * (1 + math.erf(d2 / math.sqrt(2)))))


def paper_backtest_equity_curve(seed: int = 42, points: int = 252) -> pd.Series:
    rng = np.random.default_rng(seed)
    daily = rng.standard_normal(points) * 0.012
    equity = 100_000 * np.cumprod(1 + daily)
    idx = pd.date_range(end=datetime.now(), periods=points, freq="B")
    return pd.Series(equity, index=idx[: len(equity)])
