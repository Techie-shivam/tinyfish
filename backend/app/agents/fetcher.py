from app.schemas.state import AuditState
from app.services import tinyfish


def run(state: AuditState) -> None:
    """Fetcher: get the page the way an AI tool would extract it."""
    state.fetch = tinyfish.fetch_page(state.url)
