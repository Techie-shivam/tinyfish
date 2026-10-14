"""Closed loop: re-fetch the live page after the owner applies fixes and see which gaps closed."""
from app.agents import fetcher, missing_facts, visitor
from app.schemas.state import AuditState, Verification


def verify(state: AuditState) -> Verification:
    fresh = AuditState(url=state.url)
    fetcher.run(fresh)
    visitor.run(fresh)
    missing_facts.run(fresh)
    before = {g.fact for g in state.gaps}
    after = {g.fact for g in fresh.gaps}
    result = Verification(
        closed=sorted(before - after), still_open=sorted(before & after), new=sorted(after - before),
        readability_before=state.readability, readability_after=fresh.readability,
    )
    state.verifications.append(result)
    return result
