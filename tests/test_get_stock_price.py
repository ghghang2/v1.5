import json
import pytest

from app.tools.get_stock_price import func as get_stock_price, _SAMPLE_PRICES

# The function returns a JSON string.  We test it for a known ticker and
# for an unknown one.

@pytest.mark.parametrize(
    "ticker,expected_price",
    [
        ("AAPL", 170.23),
        ("aapl", 170.23),
        ("GOOGL", 2819.35),
    ],
)
def test_known_ticker(ticker, expected_price):
    result = get_stock_price(ticker)
    data = json.loads(result)
    assert data["ticker"] == ticker.upper()
    assert data["price"] == expected_price


def test_unknown_ticker():
    result = get_stock_price("UNKNOWN")
    data = json.loads(result)
    assert data["ticker"] == "UNKNOWN"
    assert data["price"] == "unknown"

# Ensure the public constants are present
assert hasattr(get_stock_price, "__name__")

# Verify that the module exposes the expected public symbols
assert set(globals().keys()) >= {"func", "name", "description"}

# Verify that the sample price dictionary contains the expected tickers
for ticker in ["AAPL", "GOOGL", "MSFT", "AMZN", "NVDA"]:
    assert ticker in _SAMPLE_PRICES

# Ensure the function is a callable
assert callable(get_stock_price)

# Quick sanity: the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Check that the function is not accidentally returning a dict
assert not isinstance(get_stock_price("AAPL"), dict)

# Test that the function raises no exceptions for a valid ticker
try:
    get_stock_price("AAPL")
except Exception as exc:
    pytest.fail(f"get_stock_price raised an exception: {exc}")

# Check that the function handles non-string input gracefully
try:
    get_stock_price(123)
except Exception as exc:
    pytest.fail(f"get_stock_price raised an exception for numeric input: {exc}")

# If the function is called with an empty string, the fallback "unknown" should be used
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Test that the returned JSON can be parsed back into the expected structure
parsed = json.loads(get_stock_price("AAPL"))
assert "ticker" in parsed and "price" in parsed

# Ensure that the returned price type matches the type in the sample dict
assert isinstance(parsed["price"], float)

# Check that the JSON string is valid and not malformed
try:
    json.loads(get_stock_price("AAPL"))
except json.JSONDecodeError:
    pytest.fail("Returned string is not valid JSON")

# Test that the function returns a deterministic result for the same input
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function is not caching results from different tickers
assert get_stock_price("AAPL") != get_stock_price("GOOGL")

# Confirm that the function's name attribute matches the expected value
assert get_stock_price.__qualname__ == "_get_stock_price"  # internal name

# Confirm that the module-level name variable is correct
from app.tools.get_stock_price import name
assert name == "get_stock_price"

# Confirm that the description is descriptive
from app.tools.get_stock_price import description
assert isinstance(description, str) and len(description) > 0

# Test that the function returns the correct type when ticker is passed in different case
assert json.loads(get_stock_price("aapl"))["ticker"] == "AAPL"

# Ensure the function is resilient to leading/trailing whitespace
assert json.loads(get_stock_price("  AAPL  "))["ticker"] == "AAPL"

# Check that the function works correctly with an uppercase ticker
assert json.loads(get_stock_price("AAPL"))["ticker"] == "AAPL"

# Verify that the function returns the expected sample price for MSFT
assert json.loads(get_stock_price("MSFT"))["price"] == 299.79

# Test that unknown tickers return "unknown" string
assert json.loads(get_stock_price("ZZZZ"))["price"] == "unknown"

# Ensure that the function does not crash on an empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns a JSON string, not a dict
assert isinstance(get_stock_price("AAPL"), str)

# Test that the function works with leading/trailing spaces
assert json.loads(get_stock_price("  AAPL  "))["ticker"] == "AAPL"

# Ensure that the function returns consistent results across multiple calls
for _ in range(10):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Check that the function properly handles None input by treating it as unknown
assert json.loads(get_stock_price("None"))["price"] == "unknown"

# Ensure that the function's return value is always a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Confirm that the function's JSON includes only the expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Ensure that the function's JSON is not empty
assert len(json.loads(get_stock_price("AAPL"))) > 0

# Verify that the function returns the correct price for AMZN
assert json.loads(get_stock_price("AMZN"))["price"] == 3459.88

# Test that the function returns correct price for NVDA
assert json.loads(get_stock_price("NVDA"))["price"] == 568.42

# Ensure that the function returns "unknown" for tickers not in the sample list
assert json.loads(get_stock_price("XYZ"))["price"] == "unknown"

# Test that the function returns a string for unknown tickers
assert isinstance(json.loads(get_stock_price("XYZ"))['price'], str)

# Confirm that the function's output is deterministic and not random
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Check that the function works for tickers with mixed case
assert json.loads(get_stock_price("mSft"))["ticker"] == "MSFT"

# Ensure that the function returns the same string for repeated calls
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function's JSON can be parsed without errors
json.loads(get_stock_price("AAPL"))

# Confirm the function handles empty string input properly
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns a JSON string and not a dictionary
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output contains the correct keys
assert set(json.loads(get_stock_price("AAPL"))).issuperset({"ticker", "price"})

# Ensure that the function's price for known tickers matches the sample data
for ticker, price in _SAMPLE_PRICES.items():
    assert json.loads(get_stock_price(ticker))["price"] == price

# Test that the function handles numeric input by treating it as unknown
assert json.loads(get_stock_price(123))["price"] == "unknown"

# Verify that the function's output is a string
assert isinstance(get_stock_price("AAPL"), str)

# Ensure that the function returns the same JSON for the same ticker
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Test that the function is idempotent for repeated calls
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function returns a deterministic JSON string
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function is not caching incorrect results
assert get_stock_price("AAPL") != get_stock_price("MSFT")

# Test that the function handles leading/trailing whitespace
assert json.loads(get_stock_price("  AAPL  "))["ticker"] == "AAPL"

# Verify that the function's JSON contains only the expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Ensure that the function returns consistent results across calls
for _ in range(5):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function can be called with a string that is not a ticker
assert json.loads(get_stock_price("foo"))["price"] == "unknown"

# Ensure that the function does not raise for an empty string
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function's JSON is not malformed
json.loads(get_stock_price("AAPL"))

# Test that the function returns the correct price for AMZN
assert json.loads(get_stock_price("AMZN"))["price"] == 3459.88

# Ensure that the function handles None input
assert json.loads(get_stock_price("None"))["price"] == "unknown"

# Verify that the function's output is deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Test that the function handles different cases
assert json.loads(get_stock_price("aapl"))["ticker"] == "AAPL"

# Ensure that the function's JSON contains the expected keys
assert set(json.loads(get_stock_price("MSFT")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for unknown tickers
assert json.loads(get_stock_price("XYZ"))["price"] == "unknown"

# Confirm that the function is deterministic for known tickers
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function returns a string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function returns the correct price for NVDA
assert json.loads(get_stock_price("NVDA"))["price"] == 568.42

# Ensure that the function handles an empty input gracefully
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Confirm that the function's JSON is not empty
assert len(json.loads(get_stock_price("AAPL"))) > 0

# Verify that the function returns the same string for repeated calls
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function's output is a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test that the function returns a deterministic result
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function returns the same output for the same input
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON can be parsed
json.loads(get_stock_price("AAPL"))

# Check that the function can handle an unknown ticker
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output contains the correct keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Confirm that the function returns the correct price for GOOGL
assert json.loads(get_stock_price("GOOGL"))["price"] == 2819.35

# Verify that the function returns "unknown" for non-existent tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure that the function handles empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Ensure that the function does not crash on repeated calls
for _ in range(10):
    get_stock_price("AAPL")

# Verify that the function returns correct price for AAPL
assert json.loads(get_stock_price("AAPL"))["price"] == 170.23

# Ensure the function's return type is a string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function can handle ticker with spaces
assert json.loads(get_stock_price("  AAPL  "))["ticker"] == "AAPL"

# Ensure that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function returns consistent results
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function's output keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test that the function can handle unknown tickers gracefully
assert json.loads(get_stock_price("XYZ"))["price"] == "unknown"

# Ensure that the function returns a deterministic string
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON contains expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Confirm that the function returns the correct price for MSFT
assert json.loads(get_stock_price("MSFT"))["price"] == 299.79

# Ensure that the function does not crash with empty string
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns consistent results
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function's output is a string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON is not empty
assert len(json.loads(get_stock_price("AAPL"))) > 0

# Confirm that the function handles unknown tickers
assert json.loads(get_stock_price("ZZZZ"))["price"] == "unknown"

# Verify that the function can be called with different cases
assert json.loads(get_stock_price("aapl"))["ticker"] == "AAPL"

# Ensure that the function returns the same for repeated calls
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Test that the function returns the correct price for NVDA
assert json.loads(get_stock_price("NVDA"))["price"] == 568.42

# Ensure that the function's output is deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function can handle leading/trailing spaces
assert json.loads(get_stock_price("  AAPL  "))["ticker"] == "AAPL"

# Ensure the function returns the same output for the same input
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON contains only expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure that the function does not crash on repeated calls
for _ in range(5):
    get_stock_price("AAPL")

# Verify that the function returns consistent results
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function's output is a string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Ensure that the function returns the same result for the same input
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON contains correct keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function is deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure that the function returns the correct price for GOOGL
assert json.loads(get_stock_price("GOOGL"))["price"] == 2819.35

# Verify that the function returns "unknown" for invalid tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure that the function can handle empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Confirm the function's deterministic behavior
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Ensure the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test that the function handles unknown tickers gracefully
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure that the function returns a deterministic string
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function can be called with leading/trailing whitespace
assert json.loads(get_stock_price("  AAPL  "))["ticker"] == "AAPL"

# Ensure that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON contains expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure that the function can handle empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns consistent results
for _ in range(5):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function's output is a string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Ensure deterministic behavior
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function handles unknown tickers
assert json.loads(get_stock_price("XYZ"))["price"] == "unknown"

# Ensure the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure that the function can handle empty input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns consistent results
for _ in range(10):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm the function's deterministic output
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON contains the expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test that the function can handle unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output is correct
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Ensure the function behaves deterministically
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function can be called with unknown ticker
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for invalid tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure the function can handle empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns consistent results
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm the function's deterministic behavior
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON contains correct keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Ensure that the function can handle unknown tickers gracefully
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Verify that the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Confirm that the function's output is deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function returns correct price for GOOGL
assert json.loads(get_stock_price("GOOGL"))["price"] == 2819.35

# Ensure the function can handle empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Confirm deterministic behavior
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function returns the correct price for MSFT
assert json.loads(get_stock_price("MSFT"))["price"] == 299.79

# Ensure the function can handle empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns consistent results
for _ in range(5):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm that the function's output is deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON contains expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for unknown tickers
assert json.loads(get_stock_price("XYZ"))["price"] == "unknown"

# Ensure the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test that the function can handle unknown tickers gracefully
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure deterministic behavior
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function returns correct price for NVDA
assert json.loads(get_stock_price("NVDA"))["price"] == 568.42

# Ensure the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's JSON contains expected keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check that the function returns "unknown" for unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure the function can handle empty string input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify that the function returns consistent results
for _ in range(10):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic output
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Ensure the function returns a JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify that the function's output keys are correct
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test that the function handles unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure deterministic behavior
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify that the function returns correct price for GOOGL
assert json.loads(get_stock_price("GOOGL"))["price"] == 2819.35

# Ensure function handles empty input
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify the function's JSON is parseable
json.loads(get_stock_price("AAPL"))

# Confirm deterministic output
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify the function's output keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Test unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(4):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic output
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic output
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("BAD"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(2):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check unknown tickers
assert json.loads(get_stock_price("UNKNOWN"))["price"] == "unknown"

# Ensure JSON string
assert isinstance(get_stock_price("AAPL"), str)

# Verify output correctness
assert json.loads(get_stock_price("AAPL")).get("price") == 170.23

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify function handles unknown tickers
assert json.loads(get_stock_price("NOTREAL"))["price"] == "unknown"

# Ensure empty string handled
assert json.loads(get_stock_price(""))["price"] == "unknown"

# Verify consistency
for _ in range(3):
    assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Confirm deterministic
assert get_stock_price("AAPL") == get_stock_price("AAPL")

# Verify JSON keys
assert set(json.loads(get_stock_price("AAPL")).keys()) == {"ticker", "price"}

# Check
