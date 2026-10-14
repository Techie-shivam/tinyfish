"""Visitor: loads a page in a real browser and returns the human-visible text."""
from playwright.sync_api import sync_playwright

from app.schemas.state import AuditState, RenderState
from app.services import tinyfish
from app.services.text import lines, normalize

_EXPANDERS = '[role="tab"], summary, [aria-expanded="false"], [data-toggle], .accordion button, .tab'
_JS_COUNT_NOALT = "() => [...document.images].filter(i => !i.alt && i.naturalWidth > 150).length"


def render(url: str) -> RenderState:
    try:
        with sync_playwright() as pw:
            try:
                browser = pw.chromium.connect_over_cdp(tinyfish.open_browser_session(url))
                ctx = browser.contexts[0] if browser.contexts else browser.new_context()
            except Exception:  # noqa: BLE001 - fall back to local headless Chromium
                browser = pw.chromium.launch(headless=True)
                ctx = browser.new_context()
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.goto(url, wait_until="networkidle", timeout=45000)
            before = page.inner_text("body")
            for el in page.query_selector_all(_EXPANDERS)[:25]:
                try:
                    el.click(timeout=800)
                except Exception:  # noqa: BLE001 - non-clickable elements are fine to skip
                    pass
            page.wait_for_timeout(500)
            after = page.inner_text("body")
            noalt = page.evaluate(_JS_COUNT_NOALT)
            browser.close()
    except Exception as exc:  # noqa: BLE001
        return RenderState(error=f"Render failed: {exc}")
    seen = {normalize(ln) for ln in lines(before)}
    extra = [ln for ln in lines(after) if normalize(ln) not in seen]
    return RenderState(text=before, expanded_text="\n".join(extra), images_without_alt=noalt)


def run(state: AuditState) -> None:
    state.render = render(state.url)
