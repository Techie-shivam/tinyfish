"""Control group: runs the same rendered-vs-fetched check on the pages that outrank the user."""
from concurrent.futures import ThreadPoolExecutor

from app.agents import visitor
from app.schemas.state import AuditState, RivalCheck
from app.services.text import readability


def _check(item: tuple[str, str, int], rival_pages: dict[str, str]) -> RivalCheck:
    url, query, position = item
    fetched = rival_pages.get(url)
    if fetched is None:
        return RivalCheck(url=url, query=query, position=position, blocked=True, error="Fetch blocked or empty")
    rendered = visitor.render(url)
    if rendered.error:
        return RivalCheck(url=url, query=query, position=position, error=rendered.error)
    return RivalCheck(url=url, query=query, position=position, readability=readability(rendered.text, fetched))


def run(state: AuditState, rivals: list[tuple[str, str, int]], rival_pages: dict[str, str]) -> None:
    if not rivals:
        return
    with ThreadPoolExecutor(max_workers=3) as pool:
        state.rivals = list(pool.map(lambda r: _check(r, rival_pages), rivals))
