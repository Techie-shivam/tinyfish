"""Structured-Data: JSON-LD, Open Graph and meta tags, plus a ready-to-paste snippet for what is missing."""
import json
import re

from app.schemas.state import AuditState, StructuredState
from app.services import http

_LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', re.S | re.I)
_OG = re.compile(r'<meta[^>]+property=["\']og:([a-z:_]+)["\']', re.I)
_DESC = re.compile(r'<meta[^>]+name=["\']description["\'][^>]+content=["\']([^"\']+)', re.I)
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.S | re.I)


def _types(node) -> list[str]:
    found: list[str] = []
    if isinstance(node, list):
        for n in node:
            found += _types(n)
    elif isinstance(node, dict):
        t = node.get("@type")
        found += [t] if isinstance(t, str) else (t if isinstance(t, list) else [])
        found += _types(node.get("@graph", []))
    return found


def run(state: AuditState) -> None:
    _, html = http.get(state.url)
    types: list[str] = []
    for block in _LD.findall(html):
        try:
            types += _types(json.loads(block))
        except ValueError:
            continue
    og = sorted(set(_OG.findall(html)))
    desc = _DESC.search(html)
    title = (_TITLE.search(html).group(1).strip() if _TITLE.search(html) else state.fetch.title) or state.url
    missing = []
    if not types:
        missing.append("JSON-LD structured data")
    if not desc:
        missing.append("meta description")
    if "title" not in og or "description" not in og:
        missing.append("Open Graph title/description")
    snippet = ""
    if not types:
        snippet = '<script type="application/ld+json">\n' + json.dumps({
            "@context": "https://schema.org", "@type": "WebPage", "name": title, "url": state.url,
            "description": desc.group(1) if desc else "Describe this page in one or two plain sentences.",
        }, indent=2) + "\n</script>"
    state.structured = StructuredState(
        json_ld_types=sorted(set(types)), open_graph=og, has_description=bool(desc), missing=missing, snippet=snippet,
    )
