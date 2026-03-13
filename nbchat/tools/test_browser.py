"""Comprehensive tests for the browser tool."""

import json
import pytest
import os
from nbchat.tools.browser import browser


def parse_response(response: str) -> dict:
    """Parse JSON response from browser tool."""
    try:
        return json.loads(response)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {e}")


# === Phase 1: Input Validation Tests ===

def test_url_missing_scheme():
    """Test that URLs without scheme are auto-fixed."""
    result = browser(url="example.com")
    data = parse_response(result)
    assert data["status"] == "success"
    assert "example.com" in data["url"]


def test_url_invalid_domain():
    """Test handling of invalid domain."""
    result = browser(url="not-a-real-domain-12345.com")
    data = parse_response(result)
    assert "error" in data
    assert "hint" in data


def test_url_empty():
    """Test that empty URL is handled."""
    result = browser(url="")
    data = parse_response(result)
    assert "error" in data
    assert "URL is required" in data["error"]


def test_url_none():
    """Test that None URL is handled."""
    result = browser(url=None)
    data = parse_response(result)
    assert "error" in data


def test_url_whitespace():
    """Test that URL with whitespace is stripped and validated."""
    result = browser(url="  https://example.com  ")
    data = parse_response(result)
    assert data.get("status") == "success"


def test_url_empty_string_explicit():
    """Test that explicitly empty string URL is rejected."""
    result = browser(url="")
    data = parse_response(result)
    assert "error" in data
    assert "URL is required" in data["error"]


def test_actions_invalid_format_string():
    """Test that actions parameter must be a list of dicts, not a string."""
    result = browser(url="https://example.com", actions="not a list")
    data = parse_response(result)
    assert "error" in data
    assert "must be a list" in data["error"]


def test_actions_item_not_dict():
    """Test that each action item must be a dict."""
    result = browser(url="https://example.com", actions=[{"invalid": "action"}])
    data = parse_response(result)
    assert data.get("status") == "success"


def test_actions_list_of_strings():
    """Test that actions list containing strings is rejected."""
    result = browser(url="https://example.com", actions=["string1", "string2"])
    data = parse_response(result)
    assert "error" in data
    assert "must be a dict" in data["error"]


def test_actions_list_of_numbers():
    """Test that actions list containing numbers is rejected."""
    result = browser(url="https://example.com", actions=[1, 2, 3])
    data = parse_response(result)
    assert "error" in data
    assert "must be a dict" in data["error"]


def test_actions_empty_list():
    """Test that empty actions list is handled gracefully."""
    result = browser(url="https://example.com", actions=[])
    data = parse_response(result)
    assert data.get("status") == "success"


def test_actions_mixed_valid_invalid():
    """Test actions list with mix of valid and invalid items."""
    result = browser(url="https://example.com", actions=[{"type": "wait", "timeout": 1000}, "invalid", {"valid": True}])
    data = parse_response(result)
    assert "error" in data
    assert "must be a dict" in data["error"]


def test_wait_timeout_action():
    """Test wait action with timeout."""
    result = browser(url="https://example.com", actions=[{"type": "wait", "timeout": 1000}])
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "waited" in str(data.get("actions", []))


def test_actions_without_type_is_skipped():
    """Test that actions without type are logged as skipped."""
    result = browser(url="https://example.com", actions=[{}])
    data = parse_response(result)
    assert data.get("status") == "success"
    actions = data.get("actions", [])
    assert len(actions) == 1
    assert "unknown action type" in actions[0]


# === Phase 2: Basic Functionality Tests ===

def test_click_action_simple():
    """Test simple click action on a page with links."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "click", "selector": "h1"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


# === Phase 2.1: Click Action Tests ===

def test_click_action_h1_example_com():
    """Test clicking on h1 element."""
    result = browser(url="https://example.com", actions=[{"type": "click", "selector": "h1"}])
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "clicked" in str(data.get("actions", []))


def test_click_action_link_example_com():
    """Test clicking on a link element."""
    result = browser(url="https://example.com", actions=[{"type": "click", "selector": "a"}])
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "clicked" in str(data.get("actions", []))


def test_click_action_timeout_missing():
    """Test clicking on a non-existent element (should timeout gracefully)."""
    result = browser(url="https://example.com", actions=[{"type": "click", "selector": ".nonexistent-xyz123"}])
    data = parse_response(result)
    assert data.get("status") == "success"
    actions = data.get("actions", [])
    timeout_found = any("TIMEOUT" in str(a) for a in actions)
    assert timeout_found, "Expected timeout to be logged"


# === Phase 2.2: Type Action Tests ===

def test_type_action_input_field():
    """Test typing into an input field."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "type", "selector": "input", "text": "Hello World"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "typed" in str(data.get("actions", []))


def test_type_action_empty_text():
    """Test typing with empty text."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "type", "selector": "input", "text": ""}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


def test_type_action_missing_selector():
    """Test typing with missing selector."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "type", "text": "Hello"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


def test_type_action_missing_text():
    """Test typing with missing text."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "type", "selector": "input"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


# === Phase 2.3: Select Action Tests ===

def test_select_action_option():
    """Test selecting an option from a select element."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "select", "selector": "select", "value": "option1"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "selected" in str(data.get("actions", []))


def test_select_action_missing_selector():
    """Test selecting with missing selector."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "select", "value": "option1"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


# === Phase 2.4: Wait Action Tests ===

def test_wait_action_timeout():
    """Test waiting for a timeout period."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "wait", "timeout": 2000}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "waited" in str(data.get("actions", []))


def test_wait_action_missing_timeout():
    """Test waiting with missing timeout."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "wait"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


def test_wait_action_both_timeout_and_selector():
    """Test waiting with both timeout and selector."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "wait", "selector": "h1", "timeout": 5000}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "waited for" in str(data.get("actions", []))


# === Phase 2.5: Scroll Action Tests ===

def test_scroll_action_down():
    """Test scrolling down."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "scroll", "direction": "down", "amount": 500}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


def test_scroll_action_up():
    """Test scrolling up."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "scroll", "direction": "up", "amount": 500}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


def test_scroll_action_default_down():
    """Test scrolling with default direction (down)."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "scroll", "amount": 500}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


# === Phase 2.6: Navigate Action Tests ===

def test_navigate_action():
    """Test navigating to a different page."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "navigate", "url": "https://httpbin.org/get"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "navigated" in str(data.get("actions", []))


def test_navigate_action_missing_url():
    """Test navigating with missing URL."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "navigate"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


# === Phase 2.7: Screenshot Action Tests ===

def test_screenshot_action():
    """Test taking a screenshot."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "screenshot", "path": "/tmp/test_screenshot.png"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "screenshot" in str(data.get("actions", []))


def test_screenshot_missing_path():
    """Test screenshot with missing path."""
    result = browser(
        url="https://example.com",
        actions=[{"type": "screenshot"}]
    )
    data = parse_response(result)
    assert data.get("status") == "success"


# === Phase 2.8: Comprehensive Tests ===

def test_multiple_actions_sequence():
    """Test executing multiple actions in sequence."""
    result = browser(
        url="https://example.com",
        actions=[
            {"type": "wait", "timeout": 1000},
            {"type": "click", "selector": "h1"},
            {"type": "scroll", "direction": "down", "amount": 300}
        ]
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    actions = data.get("actions", [])
    assert len(actions) == 3
    assert "waited" in actions[0]
    assert "clicked" in actions[1]
    assert "scrolled" in actions[2]


def test_comprehensive_page_navigation():
    """Test comprehensive page navigation and interaction."""
    result = browser(
        url="https://example.com",
        actions=[
            {"type": "wait", "timeout": 2000},
            {"type": "click", "selector": "h1"},
            {"type": "scroll", "direction": "down", "amount": 500}
        ],
        extract_elements=True
    )
    data = parse_response(result)
    assert data.get("status") == "success"
    assert "interactive" in data or "links" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
