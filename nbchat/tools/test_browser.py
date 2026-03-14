"""Comprehensive tests for the browser tool.

Structure
---------
Unit tests (mocked)   – fast, hermetic, cover validation and response shaping
Integration tests     – real network, marked with @pytest.mark.integration
                        run with: pytest -m integration

Run fast tests only (default):
    pytest test_browser.py

Run everything:
    pytest test_browser.py -m "integration or not integration"
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch, call
import pytest

from nbchat.tools.browser import browser


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ok(result: str) -> dict:
    """Parse and assert no top-level error."""
    data = json.loads(result)
    assert "error" not in data, f"Unexpected error: {data}"
    return data


def err(result: str) -> dict:
    """Parse and assert top-level error present."""
    data = json.loads(result)
    assert "error" in data, f"Expected error, got: {data}"
    assert "hint" in data, "Error response must include a hint"
    return data


# ---------------------------------------------------------------------------
# Playwright mock factory
#
# Returns a context-manager-compatible mock that mirrors the playwright API
# surface used by the tool, so we can test response shaping without a real
# browser.
# ---------------------------------------------------------------------------

_DEFAULT_PAGE_DATA = {
    "title": "Example Domain",
    "url": "https://example.com/",
    "text": "Example Domain\nThis domain is for use in illustrative examples.",
    "interactive": [{"role": "link", "text": "More information...", "selector": None}],
    "links": [{"text": "More information...", "href": "https://www.iana.org/domains/reserved"}],
}


def _make_playwright_mock(
    page_data: dict | None = None,
    nav_status: int = 200,
    page_url: str = "https://example.com/",
    raise_on_goto=None,
    raise_on_action=None,
):
    """Build a nested mock matching the playwright sync_playwright() API."""
    data = page_data or _DEFAULT_PAGE_DATA

    page = MagicMock()
    page.url = page_url
    page.evaluate.return_value = data
    page.goto.return_value = MagicMock(status=nav_status)
    page.locator.return_value.all_inner_texts.return_value = [data["text"]]

    if raise_on_goto:
        page.goto.side_effect = raise_on_goto
    if raise_on_action:
        page.click.side_effect = raise_on_action
        page.fill.side_effect = raise_on_action
        page.select_option.side_effect = raise_on_action

    ctx = MagicMock()
    ctx.new_page.return_value = page
    ctx.__enter__ = MagicMock(return_value=ctx)
    ctx.__exit__ = MagicMock(return_value=False)

    browser_inst = MagicMock()
    browser_inst.new_context.return_value = ctx

    playwright = MagicMock()
    playwright.chromium.launch.return_value = browser_inst
    playwright.__enter__ = MagicMock(return_value=playwright)
    playwright.__exit__ = MagicMock(return_value=False)

    return playwright, browser_inst, ctx, page


def _patch(playwright_mock):
    return patch("nbchat.tools.browser.sync_playwright", return_value=playwright_mock)


# ===========================================================================
# 1. INPUT VALIDATION  (no network needed)
# ===========================================================================

class TestInputValidation:

    def test_url_none_rejected(self):
        data = err(browser(url=None))
        assert "URL is required" in data["error"]

    def test_url_empty_string_rejected(self):
        data = err(browser(url=""))
        assert "URL is required" in data["error"]

    def test_url_whitespace_only_rejected(self):
        data = err(browser(url="   "))
        assert "URL is required" in data["error"]

    def test_url_not_a_string_rejected(self):
        data = err(browser(url=42))
        assert "must be a string" in data["error"]

    def test_url_missing_scheme_is_autofixed(self):
        """scheme-less URLs should be retried with https:// prepended."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="example.com"))
        # The tool auto-prepends https:// and the mock succeeds
        goto_url = page.goto.call_args[0][0]
        assert goto_url.startswith("https://")

    def test_url_whitespace_stripped(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="  https://example.com  "))
        goto_url = page.goto.call_args[0][0]
        assert goto_url == "https://example.com"

    def test_actions_not_a_list_rejected(self):
        data = err(browser(url="https://example.com", actions="click something"))
        assert "must be a list" in data["error"]

    def test_actions_item_not_a_dict_rejected(self):
        data = err(browser(url="https://example.com", actions=["string"]))
        assert "must be a dict" in data["error"]

    def test_actions_item_number_rejected(self):
        data = err(browser(url="https://example.com", actions=[1, 2]))
        assert "must be a dict" in data["error"]

    def test_actions_mixed_valid_invalid_rejected(self):
        data = err(browser(url="https://example.com", actions=[{"type": "wait", "timeout": 100}, "bad"]))
        assert "must be a dict" in data["error"]

    def test_actions_empty_list_accepted(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", actions=[]))
        assert data["status"] == "success"
        assert "actions" not in data  # empty log omitted

    def test_actions_dict_without_type_is_treated_as_unknown(self):
        """A dict action missing 'type' gets type='' and is logged as unknown."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", actions=[{}]))
        assert data["status"] == "success"
        actions = data.get("actions", [])
        assert len(actions) == 1
        assert "unknown action type" in actions[0]

    def test_kwargs_fallback_used_when_url_missing(self):
        """If url is absent, the tool falls back to url inside the kwargs JSON blob."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url=None, kwargs=json.dumps({"url": "https://example.com"})))
        assert data["status"] == "success"

    def test_valid_url_never_overwritten_by_kwargs(self):
        """A valid url argument must not be replaced by kwargs content."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            browser(
                url="https://example.com",
                kwargs=json.dumps({"url": "https://evil.com"}),
            )
        goto_url = page.goto.call_args[0][0]
        assert "evil.com" not in goto_url


# ===========================================================================
# 2. RESPONSE SHAPING
# ===========================================================================

class TestResponseShape:

    def test_success_response_has_required_keys(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com"))
        assert {"status", "url", "title", "content"} <= data.keys()

    def test_status_is_success_when_no_actions_fail(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com"))
        assert data["status"] == "success"

    def test_status_is_partial_when_action_fails(self):
        """Any action error must flip status to 'partial'."""
        from playwright.sync_api import TimeoutError as PWTimeout
        pw, bi, ctx, page = _make_playwright_mock(raise_on_action=PWTimeout("timed out"))
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "click", "selector": ".nonexistent"}],
            ))
        assert data["status"] == "partial"
        assert "action_errors" in data
        assert any("TIMEOUT" in e for e in data["action_errors"])

    def test_action_errors_field_populated_on_failure(self):
        from playwright.sync_api import TimeoutError as PWTimeout
        pw, bi, ctx, page = _make_playwright_mock(raise_on_action=PWTimeout("timed out"))
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "click", "selector": ".nope"}],
            ))
        assert isinstance(data["action_errors"], list)
        assert len(data["action_errors"]) > 0

    def test_action_log_still_present_on_partial(self):
        """actions log must be returned even when some actions error."""
        from playwright.sync_api import TimeoutError as PWTimeout
        pw, bi, ctx, page = _make_playwright_mock(raise_on_action=PWTimeout("timed out"))
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "click", "selector": ".nope"}],
            ))
        assert "actions" in data

    def test_content_truncated_to_max_content_length(self):
        long_data = dict(_DEFAULT_PAGE_DATA)
        long_data["text"] = "x" * 20_000
        pw, bi, ctx, page = _make_playwright_mock(page_data=long_data)
        with _patch(pw):
            data = ok(browser(url="https://example.com", max_content_length=100))
        assert len(data["content"]) <= 100

    def test_title_present_without_selector(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com"))
        assert data["title"] == _DEFAULT_PAGE_DATA["title"]

    def test_title_absent_when_selector_used(self):
        """When selector= is set, result shape differs: no 'title' key."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", selector="h1"))
        assert "title" not in data
        assert "content" in data

    def test_selector_branch_does_not_raise_nameerror(self):
        """Regression: selector branch must not NameError on 'data'."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            # Should not raise; previously crashed with NameError on `data`
            result = browser(url="https://example.com", selector="h1")
        assert json.loads(result)  # valid JSON returned

    def test_extract_elements_false_omits_interactive_links(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", extract_elements=False))
        assert "interactive" not in data
        assert "links" not in data

    def test_extract_elements_true_includes_both_fields(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", extract_elements=True))
        assert "interactive" in data
        assert "links" in data

    def test_url_field_reflects_post_navigation_url(self):
        """url in response must come from page.url, not the original argument."""
        pw, bi, ctx, page = _make_playwright_mock(page_url="https://example.com/redirected")
        with _patch(pw):
            data = ok(browser(url="https://example.com"))
        assert data["url"] == "https://example.com/redirected"

    def test_error_response_always_has_hint(self):
        data = err(browser(url=""))
        assert data["hint"]  # non-empty string

    def test_http_403_returns_error(self):
        pw, bi, ctx, page = _make_playwright_mock(nav_status=403)
        with _patch(pw):
            data = err(browser(url="https://example.com"))
        assert "403" in data["error"]

    def test_http_404_returns_error(self):
        pw, bi, ctx, page = _make_playwright_mock(nav_status=404)
        with _patch(pw):
            data = err(browser(url="https://example.com"))
        assert "404" in data["error"]

    def test_http_429_returns_error(self):
        pw, bi, ctx, page = _make_playwright_mock(nav_status=429)
        with _patch(pw):
            data = err(browser(url="https://example.com"))
        assert "429" in data["error"]

    def test_http_500_returns_error(self):
        pw, bi, ctx, page = _make_playwright_mock(nav_status=500)
        with _patch(pw):
            data = err(browser(url="https://example.com"))
        assert "500" in data["error"]


# ===========================================================================
# 3. ACTION BEHAVIOUR  (mocked)
# ===========================================================================

class TestActions:

    def _run(self, actions, page_data=None):
        pw, bi, ctx, page = _make_playwright_mock(page_data=page_data)
        with _patch(pw):
            data = ok(browser(url="https://example.com", actions=actions))
        return data, page

    def test_click_calls_page_click(self):
        data, page = self._run([{"type": "click", "selector": "h1"}])
        page.click.assert_called_once_with("h1", timeout=5000)
        assert "clicked 'h1'" in data["actions"]

    def test_type_calls_page_fill(self):
        data, page = self._run([{"type": "type", "selector": "input", "text": "hello"}])
        page.fill.assert_called_once_with("input", "hello", timeout=5000)
        assert "typed into 'input'" in data["actions"]

    def test_type_empty_text_is_action_error(self):
        """Empty text triggers ValueError — should be partial, not success."""
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "type", "selector": "input", "text": ""}],
            ))
        assert data["status"] == "partial"
        assert any("ERROR" in e for e in data["action_errors"])

    def test_type_missing_selector_is_action_error(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "type", "text": "hello"}],
            ))
        assert data["status"] == "partial"

    def test_type_missing_text_is_action_error(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "type", "selector": "input"}],
            ))
        assert data["status"] == "partial"

    def test_select_calls_page_select_option(self):
        data, page = self._run([{"type": "select", "selector": "select", "value": "opt1"}])
        page.select_option.assert_called_once_with("select", value="opt1", timeout=5000)

    def test_select_missing_selector_is_action_error(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(
                url="https://example.com",
                actions=[{"type": "select", "value": "opt1"}],
            ))
        assert data["status"] == "partial"

    def test_wait_with_timeout_calls_wait_for_timeout(self):
        data, page = self._run([{"type": "wait", "timeout": 1000}])
        page.wait_for_timeout.assert_called_once_with(1000)
        assert any("waited 1000ms" in a for a in data["actions"])

    def test_wait_with_selector_calls_wait_for_selector(self):
        data, page = self._run([{"type": "wait", "selector": "h1"}])
        page.wait_for_selector.assert_called_with("h1", timeout=5000)
        assert any("waited for 'h1'" in a for a in data["actions"])

    def test_wait_with_both_selector_and_timeout_prefers_selector(self):
        """selector takes priority when both are given."""
        data, page = self._run([{"type": "wait", "selector": "h1", "timeout": 5000}])
        page.wait_for_selector.assert_called()
        assert any("waited for" in a for a in data["actions"])

    def test_wait_missing_both_is_action_error(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", actions=[{"type": "wait"}]))
        assert data["status"] == "partial"

    def test_scroll_down_evaluates_positive_scrollby(self):
        data, page = self._run([{"type": "scroll", "direction": "down", "amount": 500}])
        page.evaluate.assert_any_call("window.scrollBy(0, 500)")

    def test_scroll_up_evaluates_negative_scrollby(self):
        data, page = self._run([{"type": "scroll", "direction": "up", "amount": 300}])
        page.evaluate.assert_any_call("window.scrollBy(0, -300)")

    def test_scroll_default_direction_is_down(self):
        data, page = self._run([{"type": "scroll", "amount": 200}])
        page.evaluate.assert_any_call("window.scrollBy(0, 200)")

    def test_navigate_calls_goto_with_new_url(self):
        data, page = self._run([{"type": "navigate", "url": "https://httpbin.org/get"}])
        calls = [c[0][0] for c in page.goto.call_args_list]
        assert "https://httpbin.org/get" in calls
        assert any("navigated to" in a for a in data["actions"])

    def test_navigate_missing_url_is_action_error(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            data = ok(browser(url="https://example.com", actions=[{"type": "navigate"}]))
        assert data["status"] == "partial"

    def test_screenshot_calls_page_screenshot(self):
        data, page = self._run([{"type": "screenshot", "path": "/tmp/shot.png"}])
        page.screenshot.assert_called_once_with(path="/tmp/shot.png")
        assert any("screenshot saved" in a for a in data["actions"])

    def test_screenshot_default_path(self):
        data, page = self._run([{"type": "screenshot"}])
        page.screenshot.assert_called_once_with(path="screenshot.png")

    def test_unknown_action_type_logged_not_errored(self):
        """Unknown types appear in actions log but do NOT trigger partial status."""
        data, page = self._run([{"type": "hover", "selector": "h1"}])
        assert data["status"] == "success"
        assert any("unknown action type 'hover'" in a for a in data["actions"])
        assert "action_errors" not in data

    def test_multiple_action_log_entries_ordered(self):
        data, page = self._run([
            {"type": "wait", "timeout": 100},
            {"type": "click", "selector": "h1"},
            {"type": "scroll", "direction": "down", "amount": 100},
        ])
        log = data["actions"]
        assert len(log) == 3
        assert "waited" in log[0]
        assert "clicked" in log[1]
        assert "scrolled" in log[2]


# ===========================================================================
# 4. RESOURCE MANAGEMENT
# ===========================================================================

class TestResourceManagement:

    def test_browser_closed_on_success(self):
        pw, bi, ctx, page = _make_playwright_mock()
        with _patch(pw):
            browser(url="https://example.com")
        bi.close.assert_called_once()
        ctx.close.assert_called_once()

    def test_browser_closed_on_extraction_exception(self):
        """Browser must be cleaned up even if content extraction raises."""
        pw, bi, ctx, page = _make_playwright_mock()
        page.evaluate.side_effect = RuntimeError("extraction boom")
        with _patch(pw):
            result = browser(url="https://example.com")
        # Returns an error (caught by outer try/except), but close still ran
        ctx.close.assert_called_once()
        bi.close.assert_called_once()


# ===========================================================================
# 5. INTEGRATION TESTS  (real network, opt-in)
# ===========================================================================

@pytest.mark.integration
class TestIntegration:
    """Real browser + real network. Run with: pytest -m integration"""

    def test_example_com_loads(self):
        data = ok(browser(url="https://example.com"))
        assert data["status"] == "success"
        assert "Example Domain" in data["title"]
        assert "Example Domain" in data["content"]
        assert data["url"].startswith("https://example.com")

    def test_missing_scheme_autofixed(self):
        data = ok(browser(url="example.com"))
        assert data["status"] == "success"

    def test_invalid_domain_returns_error(self):
        data = err(browser(url="https://not-a-real-domain-xyz-12345.com"))
        assert "hint" in data

    def test_extract_elements_true_returns_both_fields(self):
        data = ok(browser(url="https://example.com", extract_elements=True))
        assert "interactive" in data
        assert "links" in data
        assert isinstance(data["interactive"], list)
        assert isinstance(data["links"], list)

    def test_extract_elements_false_omits_both_fields(self):
        data = ok(browser(url="https://example.com", extract_elements=False))
        assert "interactive" not in data
        assert "links" not in data

    def test_selector_branch_returns_content_no_title(self):
        data = ok(browser(url="https://example.com", selector="h1"))
        assert "content" in data
        assert "title" not in data
        assert "Example Domain" in data["content"]

    def test_click_h1_succeeds(self):
        data = ok(browser(
            url="https://example.com",
            actions=[{"type": "click", "selector": "h1"}],
        ))
        assert data["status"] == "success"
        assert any("clicked" in a for a in data.get("actions", []))

    def test_click_nonexistent_selector_is_partial(self):
        data = ok(browser(
            url="https://example.com",
            actions=[{"type": "click", "selector": ".xyz-does-not-exist-abc"}],
        ))
        assert data["status"] == "partial"
        assert "action_errors" in data

    def test_navigate_action_url_updates(self):
        data = ok(browser(
            url="https://example.com",
            actions=[{"type": "navigate", "url": "https://example.org"}],
        ))
        assert data["status"] == "success"
        assert "example.org" in data["url"]

    def test_wait_timeout(self):
        data = ok(browser(
            url="https://example.com",
            actions=[{"type": "wait", "timeout": 500}],
        ))
        assert data["status"] == "success"
        assert any("waited 500ms" in a for a in data.get("actions", []))

    def test_scroll_down(self):
        data = ok(browser(
            url="https://example.com",
            actions=[{"type": "scroll", "direction": "down", "amount": 300}],
        ))
        assert data["status"] == "success"

    def test_max_content_length_respected(self):
        data = ok(browser(url="https://example.com", max_content_length=50))
        assert len(data["content"]) <= 50

    def test_screenshot_saved(self, tmp_path):
        path = str(tmp_path / "shot.png")
        data = ok(browser(
            url="https://example.com",
            actions=[{"type": "screenshot", "path": path}],
        ))
        assert data["status"] == "success"
        import os
        assert os.path.exists(path)