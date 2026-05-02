"""
Simulated portfolio analytics for §1.2 — mock prices, curves, dividends; no live feeds.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

PERF_RANGES = ("1D", "1W", "1M", "3M", "YTD", "1Y", "All")

# Trading days-ish counts per button (demo resolution)
RANGE_BARS = {
    "1D": 26,
    "1W": 35,
    "1M": 66,
    "3M": 90,
    "YTD": 120,
    "1Y": 252,
    "All": 400,
}


def business_days_back(n_calendar_days: int) -> int:
    return max(5, int(n_calendar_days * 5 / 7))


def synthetic_equity_curve(
    end_value: float,
    range_key: str,
    *,
    seed: int,
    volatility: float = 0.012,
    benchmark_beta: float = 1.05,
) -> tuple[pd.DatetimeIndex, np.ndarray, np.ndarray]:
    """ correlated random walk ending near end_value; second series = mock S&P benchmark """
    rng = np.random.default_rng(seed)
    n = RANGE_BARS.get(range_key, 120)
    if range_key == "1D":
        span = timedelta(days=1)
    elif range_key == "1W":
        span = timedelta(days=7)
    elif range_key == "1M":
        span = timedelta(days=30)
    elif range_key == "3M":
        span = timedelta(days=90)
    elif range_key == "YTD":
        days_ytd = (date.today() - date(date.today().year, 1, 1)).days
        span = timedelta(days=max(30, days_ytd))
    elif range_key == "1Y":
        span = timedelta(days=365)
    else:
        span = timedelta(days=3 * 365)

    start_dt = datetime.now() - span
    idx = pd.date_range(start_dt, periods=n, freq="h" if range_key == "1D" else "D")[:n]

    noise_p = rng.standard_normal(n) * volatility
    noise_b = rng.standard_normal(n) * volatility * 0.85
    # correlated benchmark
    bench_ret = np.cumprod(1 + np.clip(noise_b, -0.04, 0.04))
    port_ret = np.cumprod(1 + np.clip(noise_p * benchmark_beta + noise_b * 0.15, -0.05, 0.05))

    scale_p = end_value / port_ret[-1]
    scale_b = (end_value * 0.98) / bench_ret[-1]  # benchmark slightly different level

    values_p = port_ret * scale_p
    values_b = bench_ret * scale_b
    return idx, values_p, values_b


def sparkline_series(end_value: float, *, seed: int = 7, points: int = 40) -> tuple[list[float], list[datetime]]:
    rng = np.random.default_rng(seed)
    r = np.cumprod(1 + rng.standard_normal(points) * 0.008)
    r = r / r[-1] * end_value
    idx = pd.date_range(datetime.now() - timedelta(days=points), periods=points, freq="D")
    return r.tolist(), idx.to_pydatetime().tolist()


def holding_mock_price_ticker(name: str, ticker: str | None) -> tuple[float, float]:
    """Return (mock_price, mock_prev_close) from ticker hash for stable demo."""
    key = (ticker or name or "X").upper()
    h = sum(ord(c) for c in key)
    price = 20.0 + (h % 500) + (h % 100) * 0.01
    prev = price * (1 - ((h % 7) - 3) / 500)
    return round(price, 2), round(prev, 2)


def today_change_for_value(market_value: float, price: float, prev_close: float) -> tuple[float, float]:
    if prev_close <= 0 or price <= 0:
        return 0.0, 0.0
    r = price / prev_close - 1.0
    return market_value * r, r * 100.0


MOCK_DIVIDENDS = {
    "VTI": [{"ex_date": date.today() + timedelta(days=12), "amount_per_share": 0.82, "pay_date": date.today() + timedelta(days=45)}],
    "AAPL": [{"ex_date": date.today() + timedelta(days=45), "amount_per_share": 0.25, "pay_date": date.today() + timedelta(days=78)}],
    "SPY": [{"ex_date": date.today() + timedelta(days=8), "amount_per_share": 1.58, "pay_date": date.today() + timedelta(days=38)}],
}


def dividend_events_for_ticker(ticker: str | None) -> list[dict[str, Any]]:
    if not ticker:
        return []
    return MOCK_DIVIDENDS.get(ticker.upper(), [])


def analyst_mock(ticker: str | None) -> dict[str, Any]:
    if not ticker:
        return {"rating": "—", "target": "—", "count": 0}
    h = sum(ord(c) for c in ticker.upper())
    labels = ["Hold", "Buy", "Strong Buy", "Neutral"]
    return {
        "consensus": labels[h % 4],
        "price_target": 150 + (h % 200),
        "analysts": 12 + (h % 20),
    }


def news_mock_headlines(ticker: str | None, n: int = 4) -> list[str]:
    base = ticker or "markets"
    return [
        f"{base}: earnings preview — simulated headline {i+1} (not real news)."
        for i in range(n)
    ]


def earnings_dates_mock(ticker: str | None) -> tuple[date | None, date | None]:
    if not ticker:
        return None, None
    h = sum(ord(c) for c in ticker.upper())
    q = date.today() + timedelta(days=30 + (h % 60))
    return q, q + timedelta(days=45)


def net_open_unrealized(lots: list[dict], market_value: float, cost_fallback: float) -> tuple[float, float]:
    """Sum lots cost vs position; return cost_basis, unrealized."""
    if not lots:
        return cost_fallback, market_value - cost_fallback
    cost = sum(float(l.get("qty", 0)) * float(l.get("cost_per_share", 0)) for l in lots)
    return cost, market_value - cost


def ensure_default_accounts() -> list[dict[str, Any]]:
    return [
        {
            "id": "acc_main",
            "name": "Main",
            "theme": "#3498db",
            "goal_type": "General investing",
            "target_date": None,
            "goal_target_usd": None,
        }
    ]
