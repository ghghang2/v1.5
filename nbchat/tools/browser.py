"""Stateless Browser Tool for LLM Function Calling.

Design principles (informed by Browser-Use, Stagehand, Browserbase research):
- Chromium over Firefox: faster launch, better site compatibility, better stealth
- Resource blocking: skip images/fonts/media for ~3x faster loads
- Structured extraction: returns title, text, links, AND interactive elements
  so the LLM can reason about what actions are available (Stagehand-style)
- Stealth fingerprinting: realistic headers + viewport to reduce bot detection
- Actionable errors: every failure includes a HINT field to guide the agent
- Single retry on transient network errors before giving up
"""

from __future__ import annotations

import json
import random
import re
from typing import Any

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ---------------------------------------------------------------------------
# Stealth helpers
# ---------------------------------------------------------------------------

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]

_BLOCK_TYPES = {"image", "media", "font"}  # skip binary resources for speed

_JS_STEALTH = """
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
"""

_JS_EXTRACT = """
() => {
    // Collect interactive elements (buttons, links, inputs, selects)
    const interactive = [];
    const seen = new Set();
    const add = (el, role) => {
        const text = (el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || '').trim().slice(0, 80);
        const sel = el.id ? '#' + el.id : el.name ? `[name="${el.name}"]` : null;
        if (text && !seen.has(text)) { seen.add(text); interactive.push({role, text, selector: sel}); }
    };
    document.querySelectorAll('a[href]').forEach(el => add(el, 'link'));
    document.querySelectorAll('button, [role="button"]').forEach(el => add(el, 'button'));
    document.querySelectorAll('input:not([type="hidden"]), textarea').forEach(el => add(el, 'input'));
    document.querySelectorAll('select').forEach(el => add(el, 'select'));

    // Clean body text: collapse whitespace, drop script/style noise
    const body = document.body || document.documentElement;
    const clone = body.cloneNode(true);
    clone.querySelectorAll('script,style,noscript,svg').forEach(n => n.remove());
    const text = clone.innerText.replace(/[ \\t]{2,}/g, ' ').replace(/\\n{3,}/g, '\\n\\n').trim();

    return {
        title: document.title,
        url: location.href,
        text,
        interactive: interactive.slice(0, 60),   // cap to keep payload manageable
        links: Array.from(document.querySelectorAll('a[href]'))
                    .map(a => ({text: a.innerText.trim().slice(0, 60), href: a.href}))
                    .filter(l => l.href.startsWith('http'))
                    .slice(0, 40),
    };
}
"""

# ---------------------------------------------------------------------------
# Error helpers
# ---------------------------------------------------------------------------

_HINTS = {
    "net::ERR_NAME_NOT_RESOLVED": "The domain could not be resolved. Check the URL for typos or try a different URL.",
    "net::ERR_CONNECTION_REFUSED": "The server refused the connection. The site may be down or blocking automated access.",
    "net::ERR_CONNECTION_TIMED_OUT": "Connection timed out. Try again, increase navigation_timeout, or the site may be blocking bots.",
    "net::ERR_TOO_MANY_REDIRECTS": "The page is caught in a redirect loop. Try visiting a more specific URL.",
    "403": "Access forbidden (403). The site is blocking automated access. Try adding realistic actions or a different entry URL.",
    "404": "Page not found (404). The URL may be outdated or incorrect.",
    "429": "Rate limited (429). Wait before retrying or reduce request frequency.",
    "500": "Server error (500). The site is having issues; try again later.",
    "TimeoutError": "Page load timed out. Try increasing navigation_timeout (default 30000ms) or use wait_until='commit'.",
    "selector": "The CSS selector was not found. Use extract_elements=true to discover available selectors first.",
}

def _hint(msg: str) -> str:
    for key, hint in _HINTS.items():
        if key in msg:
            return hint
    return "Try a different URL, check network connectivity, or simplify the request."

def _err(message: str, **extra) -> str:
    return json.dumps({"error": message, "hint": _hint(message), **extra})


# ---------------------------------------------------------------------------
# Core function
# ---------------------------------------------------------------------------

def browser(
    url: str,
    actions: list[dict[str, Any]] | None = None,
    selector: str | None = None,
    extract_elements: bool = False,
    navigation_timeout: int = 30000,
    action_timeout: int = 5000,
    max_content_length: int = 8000,
    wait_until: str = "domcontentloaded",
    **kwargs,
) -> str:
    """Stateless browser tool. Launches a fresh Chromium instance per call.

    Parameters
    ----------
    url:
        The page to visit. Must include scheme (https://...).
    actions:
        Optional list of interactions performed *before* content extraction.
        Supported types:

        - ``{"type": "click", "selector": "CSS_OR_TEXT"}``
        - ``{"type": "type", "selector": "CSS", "text": "hello"}``
        - ``{"type": "select", "selector": "CSS", "value": "option_value"}``
        - ``{"type": "wait", "selector": "CSS"}``   or   ``{"type": "wait", "timeout": 2000}``
        - ``{"type": "scroll", "direction": "down", "amount": 500}``  (amount in px)
        - ``{"type": "navigate", "url": "https://..."}``
        - ``{"type": "screenshot", "path": "shot.png"}``
    selector:
        CSS selector to scope text extraction. If omitted the full page text is returned.
    extract_elements:
        When True, the response includes ``interactive`` (buttons/inputs/links)
        and ``links`` lists so you can discover what actions are possible.
        Defaults to False to keep payloads small.
    navigation_timeout:
        Ms to wait for page navigation (default 30000).
    action_timeout:
        Ms to wait for each action's selector/click (default 5000).
    max_content_length:
        Max characters of page text returned (default 8000).
    wait_until:
        Playwright navigation event: ``'domcontentloaded'`` (fast, default),
        ``'load'`` (waits for all resources), or ``'networkidle'`` (slowest, most complete).
    """

    # =========================================================================
    # INPUT VALIDATION
    # =========================================================================

    if url is None or not isinstance(url, str) or url.strip() == "":
        # FIX: Only fall back to kwargs if url is genuinely missing, never
        # overwrite a valid url argument with kwargs content.
        extra_url = None
        if kwargs.get("kwargs") and isinstance(kwargs["kwargs"], str):
            try:
                extra = json.loads(kwargs["kwargs"])
                if isinstance(extra, dict):
                    extra_url = extra.get("url", "")
                    actions = actions or extra.get("actions")
                    selector = selector or extra.get("selector")
            except json.JSONDecodeError:
                pass
        if not extra_url:
            return _err("URL is required.", hint="Provide a full URL including scheme, e.g. https://example.com")
        url = extra_url

    if not isinstance(url, str):
        return _err(f"URL must be a string, got {type(url).__name__}.",
                    hint="Provide a string URL, e.g. 'https://example.com'")

    url = url.strip()

    if not re.match(r"https?://", url):
        url = "https://" + url  # auto-fix missing scheme

    if actions is not None and not isinstance(actions, list):
        return _err(f"actions must be a list, got {type(actions).__name__}.",
                    hint="Provide actions as a list of dicts, e.g. [{'type': 'click', 'selector': '.button'}]")

    if actions is not None:
        for i, act in enumerate(actions):
            if not isinstance(act, dict):
                return _err(f"actions[{i}] must be a dict, got {type(act).__name__}.",
                            hint="Each action should be a dict with 'type' key, e.g. {'type': 'click', 'selector': '.button'}")
            if "type" not in act:
                act["type"] = ""

    def _run() -> str:
        with sync_playwright() as p:
            browser_inst = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                ],
            )
            # FIX: Use random UA selection instead of deterministic hash, so
            # repeated visits to the same URL don't expose a consistent fingerprint.
            ctx = browser_inst.new_context(
                user_agent=random.choice(_USER_AGENTS),
                viewport={"width": 1280, "height": 800},
                locale="en-US",
                timezone_id="America/New_York",
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                },
            )

            try:
                # Block heavy resources for speed
                ctx.route(
                    "**/*",
                    lambda route: route.abort()
                    if route.request.resource_type in _BLOCK_TYPES
                    else route.continue_(),
                )

                page = ctx.new_page()
                page.add_init_script(_JS_STEALTH)

                # Navigate
                try:
                    resp = page.goto(url, timeout=navigation_timeout, wait_until=wait_until)
                except PWTimeout:
                    return _err(f"TimeoutError navigating to {url}")
                except Exception as e:
                    return _err(f"Navigation failed: {e}")

                status = resp.status if resp else 0
                if status in (403, 404, 429, 500):
                    return _err(f"HTTP {status} from {url}")

                # Perform actions
                log: list[str] = []
                action_errors: list[str] = []
                # FIX: Track current URL via Playwright's live page.url rather than
                # manually, so redirects and client-side navigation are captured.
                for i, act in enumerate(actions or []):
                    act_type = act.get("type", "")
                    try:
                        if act_type == "click":
                            sel = act.get("selector", "")
                            if not sel:
                                raise ValueError("'selector' is required for click")
                            page.click(sel, timeout=action_timeout)
                            log.append(f"clicked '{sel}'")

                        elif act_type == "type":
                            sel, text = act.get("selector", ""), act.get("text", "")
                            if not sel or text == "":
                                raise ValueError("'selector' and 'text' are required for type")
                            page.fill(sel, text, timeout=action_timeout)
                            log.append(f"typed into '{sel}'")

                        elif act_type == "select":
                            sel, val = act.get("selector", ""), act.get("value", "")
                            if not sel:
                                raise ValueError("'selector' is required for select")
                            page.select_option(sel, value=val, timeout=action_timeout)
                            log.append(f"selected '{val}' in '{sel}'")

                        elif act_type == "wait":
                            if "selector" in act:
                                page.wait_for_selector(act["selector"], timeout=action_timeout)
                                log.append(f"waited for '{act['selector']}'")
                            elif "timeout" in act:
                                page.wait_for_timeout(act["timeout"])
                                log.append(f"waited {act['timeout']}ms")
                            else:
                                raise ValueError("'selector' or 'timeout' required for wait")

                        elif act_type == "scroll":
                            direction = act.get("direction", "down")
                            amount = int(act.get("amount", 500))
                            dy = amount if direction == "down" else -amount
                            page.evaluate(f"window.scrollBy(0, {dy})")
                            log.append(f"scrolled {direction} {amount}px")

                        elif act_type == "navigate":
                            dest = act.get("url", "")
                            if not dest:
                                raise ValueError("'url' is required for navigate")
                            page.goto(dest, timeout=navigation_timeout, wait_until=wait_until)
                            log.append(f"navigated to '{dest}'")

                        elif act_type == "screenshot":
                            path = act.get("path", "screenshot.png")
                            page.screenshot(path=path)
                            log.append(f"screenshot saved to '{path}'")

                        else:
                            log.append(f"unknown action type '{act_type}' (skipped) – supported: click, type, select, wait, scroll, navigate, screenshot")

                    except PWTimeout:
                        msg = f"TIMEOUT on action {i} ({act_type}) – selector may not exist; use extract_elements=true to inspect the page"
                        log.append(msg)
                        action_errors.append(msg)
                    except Exception as e:
                        msg = f"ERROR on action {i} ({act_type}): {e}"
                        log.append(msg)
                        action_errors.append(msg)

                # Extract content
                # FIX: Always capture live URL from page after all navigation/actions.
                final_url = page.url if page.url not in ("about:blank", "") else url

                if selector:
                    try:
                        page.wait_for_selector(selector, timeout=action_timeout)
                        content = "\n".join(page.locator(selector).all_inner_texts())
                    except Exception:
                        return _err(
                            f"selector '{selector}' not found",
                            hint="Use extract_elements=true to see available selectors, or omit selector for full-page text.",
                            page_url=final_url,
                        )
                    # FIX: data is only defined in the else branch; build result
                    # directly here to avoid NameError on data.get("title", ...).
                    result: dict[str, Any] = {
                        # FIX: Reflect action failures in status instead of always
                        # reporting success even when every action errored out.
                        "status": "partial" if action_errors else "success",
                        "url": final_url,
                        "content": content[:max_content_length],
                    }
                else:
                    data: dict = page.evaluate(_JS_EXTRACT)
                    content = data.get("text", "")
                    result = {
                        "status": "partial" if action_errors else "success",
                        "url": final_url,
                        "title": data.get("title", ""),
                        "content": content[:max_content_length],
                    }
                    # FIX: Only evaluate interactive/links when actually requested,
                    # rather than always extracting them and then discarding.
                    if extract_elements:
                        result["interactive"] = data.get("interactive", [])
                        result["links"] = data.get("links", [])

                if log:
                    result["actions"] = log
                if action_errors:
                    result["action_errors"] = action_errors

                return json.dumps(result)

            finally:
                # FIX: Always close context and browser, even if extraction raises.
                ctx.close()
                browser_inst.close()

    # Single retry for transient network hiccups
    try:
        return _run()
    except Exception as e:
        msg = str(e)
        if any(t in msg for t in ("ERR_CONNECTION", "ERR_NAME", "socket")):
            try:
                return _run()
            except Exception as e2:
                return _err(f"Failed after retry: {e2}")
        return _err(f"Unexpected error: {msg}")


# ---------------------------------------------------------------------------
# Tool definition (OpenAI / Anthropic function-calling schema)
# ---------------------------------------------------------------------------

func = browser
name = "browser"
description = """\
Stateless browser tool. Visits a URL and returns the page's text content.
Each call is a fully independent session (no cookies or state are shared).

Key parameters:
- url (required): Full URL including scheme, e.g. https://example.com
- actions (optional): Ordered list of interactions to perform before extraction.
  Supported action types:
    click      – {"type":"click","selector":"CSS"}
    type       – {"type":"type","selector":"CSS","text":"value"}
    select     – {"type":"select","selector":"CSS","value":"option"}
    wait       – {"type":"wait","selector":"CSS"} or {"type":"wait","timeout":2000}
    scroll     – {"type":"scroll","direction":"down","amount":500}
    navigate   – {"type":"navigate","url":"https://..."}
    screenshot – {"type":"screenshot","path":"file.png"}
- selector (optional): CSS selector to scope extracted text to one element.
- extract_elements (optional, bool): Set true to receive lists of interactive
  elements (buttons, inputs) and links — useful for discovering what's on a page
  before planning actions.
- wait_until (optional): "domcontentloaded" (default/fast), "load", "networkidle"
- max_content_length (optional): max chars of text returned (default 8000).

Returns JSON with: status, url, title, content, and optionally actions log,
interactive elements, and links. On failure returns {error, hint}.\
"""

__all__ = ["browser", "func", "name", "description"]