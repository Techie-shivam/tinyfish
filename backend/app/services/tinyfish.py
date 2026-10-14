"""Thin wrapper over the TinyFish SDK: Search, Fetch and Browser sessions."""
from tinyfish import TinyFish

from app.core.config import get_settings
from app.schemas.state import FetchState, SearchHit
from app.services.text import estimate_tokens

_BLOCK_MARKERS = ("captcha", "access denied", "verify you are human", "are you a robot", "cf-chl")


def _client() -> TinyFish:
    return TinyFish(api_key=get_settings().tinyfish_api_key or None)


def fetch_page(url: str) -> FetchState:
    """Fetch a page as an AI tool would extract it, recording blocks."""
    try:
        resp = _client().fetch.get_contents(
            [url], format="markdown", links=True, image_links=True,
            purpose="Audit what AI tools can read on this page",
        )
    except Exception as exc:  # noqa: BLE001 - surface any API failure as a block
        return FetchState(status=0, blocked=True, block_reason=f"Fetch failed: {exc}")
    if not resp.results:
        reason = resp.errors[0].error if resp.errors else "Fetch returned no content"
        return FetchState(status=0, blocked=True, block_reason=reason)
    r = resp.results[0]
    text = r.text or ""
    low = text[:2000].lower()
    blocked = len(text.strip()) < 200 and any(m in low for m in _BLOCK_MARKERS)
    return FetchState(
        status=200, text=text, blocked=blocked,
        block_reason="Page looks like a bot wall or captcha" if blocked else "",
        tokens=estimate_tokens(text), final_url=r.final_url or url, title=r.title or "",
        links=r.links, image_links=r.image_links,
    )


def search(query: str) -> list[SearchHit]:
    resp = _client().search.query(query, language="en")
    return [SearchHit(position=r.position, title=r.title, url=r.url, snippet=r.snippet) for r in resp.results]


def open_browser_session(url: str) -> str:
    """Create a TinyFish remote browser session and return its CDP URL."""
    return _client().browser.sessions.create(url=url, timeout_seconds=120).cdp_url
