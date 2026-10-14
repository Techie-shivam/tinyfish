import re
from urllib.parse import urlparse

_WS = re.compile(r"\s+")
_MD = re.compile(r"[*_`#>|\[\]()]")


def normalize(text: str) -> str:
    """Lowercase, strip markdown punctuation and collapse whitespace."""
    return _WS.sub(" ", _MD.sub(" ", text)).strip().lower()


def domain(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host.removeprefix("www.")


def same_site(a: str, b: str) -> bool:
    da, db = domain(a), domain(b)
    return bool(da) and (da == db or da.endswith("." + db) or db.endswith("." + da))


def lines(text: str, min_len: int = 25) -> list[str]:
    """Meaningful text lines (visible sentences/blocks) used for diffing."""
    return [ln.strip() for ln in text.splitlines() if len(ln.strip()) >= min_len]


def missing_lines(rendered: str, fetched: str, min_len: int = 25) -> list[str]:
    """Rendered lines whose text is absent from the fetched text."""
    haystack = normalize(fetched)
    return [ln for ln in lines(rendered, min_len) if normalize(ln) not in haystack]


def readability(rendered: str, fetched: str) -> float | None:
    """Share of rendered lines that Fetch can see (1.0 = fully readable)."""
    rendered_lines = lines(rendered)
    if not rendered_lines:
        return None
    return round(1 - len(missing_lines(rendered, fetched)) / len(rendered_lines), 2)


def estimate_tokens(text: str) -> int:
    return len(text) // 4
