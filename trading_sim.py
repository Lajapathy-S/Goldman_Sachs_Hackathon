"""
Simulated / educational trading helpers — no broker connectivity, not real money.
Used to demonstrate product-style flows from a spec in a safe classroom prototype.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any

# Order types named for the spec; definitions are for UI education only.
ORDER_TYPE_HELP: dict[str, str] = {
    "Market": "Fill as soon as possible at the best available price right now (simulated).",
    "Limit": "Only fill at your limit price or better.",
    "Stop-loss": "Becomes a market order if price crosses your stop (direction depends on buy/sell).",
    "Stop-limit": "Becomes a limit order after the stop is triggered.",
    "Trailing stop": "Stop price follows the market by a trail amount or percent you set.",
}

# Mock reference prices for demo (not live).
MOCK_STOCK_ETF: dict[str, float] = {
    "SPY": 450.0,
    "VOO": 480.0,
    "AAPL": 195.0,
    "MSFT": 420.0,
    "VTI": 280.0,
}

MOCK_CRYPTO: dict[str, float] = {
    "BTC": 98500.0,
    "ETH": 3650.0,
    "SOL": 185.0,
    "DOGE": 0.16,
}

OPTION_CHAIN_ROWS = [
    {"strike": 440.0, "call_bid": 8.2, "call_ask": 8.4, "put_bid": 4.1, "put_ask": 4.25, "iv": 0.18, "delta_c": 0.52, "gamma": 0.02, "theta": -0.09, "vega": 0.41, "oi": 12400, "vol": 982},
    {"strike": 445.0, "call_bid": 5.5, "call_ask": 5.65, "put_bid": 6.0, "put_ask": 6.15, "iv": 0.17, "delta_c": 0.41, "gamma": 0.025, "theta": -0.08, "vega": 0.39, "oi": 8200, "vol": 756},
    {"strike": 450.0, "call_bid": 3.6, "call_ask": 3.75, "put_bid": 8.5, "put_ask": 8.7, "iv": 0.16, "delta_c": 0.31, "gamma": 0.024, "theta": -0.07, "vega": 0.36, "oi": 15200, "vol": 1123},
]


def fractional_shares(dollar_amount: float, reference_price: float) -> tuple[float, str]:
    if reference_price <= 0:
        return 0.0, "Enter a reference price greater than zero."
    qty = dollar_amount / reference_price
    return qty, f"{qty:.6f} shares (fractional allowed)"


def next_recurring_date(
    frequency: str,
    start: date | None = None,
) -> date:
    """Next calendar execution for demo (not market hours)."""
    d0 = start or date.today()
    if frequency == "Daily":
        return d0 + timedelta(days=1)
    if frequency == "Weekly":
        return d0 + timedelta(weeks=1)
    if frequency == "Bi-weekly":
        return d0 + timedelta(weeks=2)
    if frequency == "Monthly":
        # simple: same day next month if possible
        m = d0.month + 1
        y = d0.year
        if m > 12:
            m, y = 1, y + 1
        try:
            return date(y, m, d0.day)
        except ValueError:
            return date(y, m, 28)
    return d0 + timedelta(weeks=1)


@dataclass
class ShortInfo:
    """Mock short metrics for pre-trade disclosure panel."""

    symbol: str
    borrow_rate_apy: float
    short_interest_pct: float
    days_to_cover: float


def mock_short_info(symbol: str) -> ShortInfo:
    s = sum(ord(c) for c in symbol.upper()) if symbol else 0
    return ShortInfo(
        symbol=symbol,
        borrow_rate_apy=4.2 + (s % 10) * 0.3,
        short_interest_pct=2.1 + (s % 5) * 0.2,
        days_to_cover=1.5 + (s % 8) * 0.5,
    )


def mock_futures_contract(spec: str) -> dict[str, Any]:
    return {
        "spec": spec,
        "tick_size": 0.25,
        "notional_per_point": 50 if spec in ("ES",) else 20,
        "margin_required_hint": 12000.0,
    }


def instant_deposit_limits(portfolio_value: float = 0.0) -> dict[str, float]:
    """Illustrates tiered instant buying power — examples only, not a live broker rule."""
    gold_style = min(5000.0, max(1000.0, 3.0 * portfolio_value))
    return {
        "standard_instant_ach_usd": 1000.0,
        "illustrative_tier_ceiling_usd": gold_style,
    }
