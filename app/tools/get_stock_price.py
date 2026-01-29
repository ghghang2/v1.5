# app/tools/get_stock_price.py
"""
Tool that returns a mock stock price.

The function simulates a price lookup for a given ticker.  It is used
by the Streamlit UI to demonstrate the function‑calling API.  The
implementation is intentionally simple – a hard‑coded dictionary of
sample prices – but the interface mirrors a real API call.
"""

import json
from typing import Dict

# Hard‑coded sample data – in a real system this would query a
# finance API such as Yahoo Finance or Alpha Vantage.
_SAMPLE_PRICES: Dict[str, float] = {
    "AAPL": 170.23,
    "GOOGL": 2819.35,
    "MSFT": 299.79,
    "AMZN": 3459.88,
    "NVDA": 568.42,
}


def get_stock_price(ticker: str) -> str:
    """Return the current stock price for *ticker*.

    Parameters
    ----------
    ticker:
        Stock symbol (e.g. ``"AAPL"``).  The lookup is case‑insensitive.

    Returns
    -------
    str
        JSON string containing ``ticker`` and ``price`` keys.  If the
        ticker is unknown, ``price`` is set to ``"unknown"``.
    """
    price = _SAMPLE_PRICES.get(ticker.upper(), "unknown")
    result = {"ticker": ticker.upper(), "price": price}
    return json.dumps(result)

# ---------------------------------------------------------------------------
#  Export the tool as part of the public API
# ---------------------------------------------------------------------------
__all__ = ["get_stock_price"]
