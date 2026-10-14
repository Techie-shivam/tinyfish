"""Plain HTTP helpers for what a non-browser bot receives (raw HTML, robots.txt...)."""
import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ReadabilityAuditor/1.0)"}


def get(url: str, timeout: float = 15) -> tuple[int, str]:
    """Returns (status, text); status 0 on network failure."""
    try:
        r = httpx.get(url, headers=HEADERS, timeout=timeout, follow_redirects=True)
        return r.status_code, r.text
    except httpx.HTTPError:
        return 0, ""
