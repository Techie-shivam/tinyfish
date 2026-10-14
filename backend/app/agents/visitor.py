"""Visitor: loads a page in a real browser and returns the human-visible text."""
from playwright.sync_api import sync_playwright

from app.schemas.state import AuditState, RenderState
from app.services import tinyfish
from app.services.text import lines, normalize

_EXPANDERS = '[role="tab"], summary, [aria-expanded="false"], [data-toggle], .accordion button, .tab'
_JS_COLLECT = r"""() => {
  const clip = t => t.replace(/\s+/g, ' ').trim().slice(0, 300);
  const elements = [];
  document.querySelectorAll('table').forEach(e => elements.push({kind: 'table', text: e.innerText}));
  document.querySelectorAll('[role=tabpanel]').forEach(e => elements.push({kind: 'tab', text: e.textContent}));
  document.querySelectorAll('details').forEach(e => elements.push({kind: 'accordion', text: e.textContent}));
  const noalt = [...document.images].filter(i => !i.alt && i.naturalWidth > 150);
  noalt.forEach(i => elements.push({kind: 'image', text: i.currentSrc || i.src}));
  const hidden = [];
  const skip = new Set(['SCRIPT', 'STYLE', 'NOSCRIPT', 'HEAD', 'TEMPLATE']);
  for (const e of document.body.querySelectorAll('*')) {
    if (skip.has(e.tagName)) continue;
    const own = [...e.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent).join(' ');
    const t = clip(own);
    if (t.length < 20) continue;
    const s = getComputedStyle(e), r = e.getBoundingClientRect();
    let why = '';
    if (parseFloat(s.opacity) === 0) why = 'opacity 0';
    else if (parseFloat(s.fontSize) === 0) why = 'font-size 0';
    else if (s.position !== 'static' && (r.right < 0 || r.left > innerWidth * 2 || r.bottom < 0)) why = 'positioned off-screen';
    else if (s.visibility === 'hidden') why = 'visibility hidden';
    else if (s.display === 'none') why = 'display none';
    if (why) hidden.push({text: t, reason: why});
    if (hidden.length >= 60) break;
  }
  return {elements: elements.slice(0, 80).map(x => ({kind: x.kind, text: clip(x.text)})), hidden, noalt: noalt.length};
}"""


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
            info = page.evaluate(_JS_COLLECT)
            browser.close()
    except Exception as exc:  # noqa: BLE001
        return RenderState(error=f"Render failed: {exc}")
    seen = {normalize(ln) for ln in lines(before)}
    extra = [ln for ln in lines(after) if normalize(ln) not in seen]
    return RenderState(text=before, expanded_text="\n".join(extra), images_without_alt=info["noalt"],
                       elements=info["elements"], hidden=info["hidden"])


def run(state: AuditState) -> None:
    state.render = render(state.url)
