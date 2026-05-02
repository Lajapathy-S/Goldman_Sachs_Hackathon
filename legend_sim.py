"""
Robinhood Legend–style mocks: OHLC, popular indicators, options P&L curve (teaching only).
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

INDICATOR_CATALOG = [
    ("SMA (20)", "sma20"),
    ("EMA (12)", "ema12"),
    ("RSI (14)", "rsi14"),
    ("MACD", "macd"),
    ("Bollinger Bands", "bb"),
    ("VWAP", "vwap"),
    ("Volume bars", "volume"),
]


def generate_ohlcv(bars: int = 120, seed: int = 42, start_price: float = 180.0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ret = rng.standard_normal(bars) * 0.015
    close = start_price * np.cumprod(1 + ret)
    open_ = np.empty_like(close)
    open_[0] = close[0]
    open_[1:] = close[:-1]
    noise = rng.random(bars) * 0.008
    high = np.maximum(open_, close) * (1 + noise)
    low = np.minimum(open_, close) * (1 - noise)
    vol = rng.integers(100_000, 5_000_000, size=bars)
    idx = pd.date_range(end=pd.Timestamp.now(), periods=bars, freq="h" if bars <= 48 else "D")
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": vol}, index=idx
    )


def ema(s: pd.Series, span: int) -> pd.Series:
    return s.ewm(span=span, adjust=False).mean()


def rsi_series(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = (-delta).clip(lower=0.0)
    avg_g = gain.ewm(alpha=1.0 / period, adjust=False).mean()
    avg_l = loss.ewm(alpha=1.0 / period, adjust=False).mean()
    rs = avg_g / avg_l.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd_bundle(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    macd_line = ema(close, 12) - ema(close, 26)
    signal = ema(macd_line, 9)
    hist = macd_line - signal
    return macd_line, signal, hist


def bollinger(close: pd.Series, window: int = 20, k: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    mid = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = mid + k * std
    lower = mid - k * std
    return upper, mid, lower


def vwap_series(df: pd.DataFrame) -> pd.Series:
    tp = (df["high"] + df["low"] + df["close"]) / 3.0
    vol = df["volume"].astype(float)
    return (tp * vol).cumsum() / vol.cumsum()


def option_long_call_pnl(
    underlying_prices: np.ndarray,
    strike: float,
    premium_per_share: float,
    contracts: int = 1,
    multiplier: float = 100.0,
) -> np.ndarray:
    """Intrinsic at expiry-style payoff minus premium paid (per contract)."""
    intrinsic = np.maximum(underlying_prices - strike, 0.0)
    return contracts * multiplier * (intrinsic - premium_per_share)


def option_pnl_with_decay(
    underlying_prices: np.ndarray,
    strike: float,
    premium: float,
    theta_decay_frac: float,
    vega_shock: float,
    contracts: int = 1,
    multiplier: float = 100.0,
) -> np.ndarray:
    """Toy curve: scales payoff by (1-theta) + mild IV bump narrative."""
    base = option_long_call_pnl(underlying_prices, strike, premium, contracts, multiplier)
    return base * (1.0 - theta_decay_frac) + vega_shock * contracts * multiplier * 0.02
