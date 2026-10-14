"""Orchestrates the seven agents over one shared AuditState and reports progress."""
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from app.agents import (
    control_group, fetcher, interrogator, missing_facts, query_discovery, question_miner, report_writer, visitor,
)
from app.schemas.api import AuditJob

AGENTS = ["Fetcher", "Visitor", "Missing-Facts", "Query Discovery", "Question Miner", "Interrogator",
          "Control Group", "Report Writer"]


class Progress:
    """Updates the job's per-agent status and logs timings."""

    def __init__(self, job: AuditJob) -> None:
        self.job = job

    def step(self, name: str, fn: Callable[[], object]) -> object:
        agent = next(a for a in self.job.agents if a.name == name)
        agent.status = "running"
        start = time.perf_counter()
        try:
            result = fn()
            agent.status = "done"
            return result
        except Exception as exc:  # noqa: BLE001 - keep the audit going; the failure is shown on the agent
            agent.status, agent.detail = "failed", str(exc)[:200]
            return None
        finally:
            self.job.state.timings[name] = round(time.perf_counter() - start, 1)


def run_audit(job: AuditJob) -> None:
    state, p = job.state, Progress(job)
    job.status = "running"
    try:
        with ThreadPoolExecutor(max_workers=2) as pool:  # Fetcher and Visitor run in parallel
            futures = [pool.submit(p.step, "Fetcher", lambda: fetcher.run(state)),
                       pool.submit(p.step, "Visitor", lambda: visitor.run(state))]
            for f in futures:
                f.result()
        p.step("Missing-Facts", lambda: missing_facts.run(state))
        p.step("Query Discovery", lambda: query_discovery.run(state))
        rival_pages: dict[str, str] = {}
        rivals = p.step("Question Miner", lambda: question_miner.run(state, rival_pages)) or []
        p.step("Interrogator", lambda: interrogator.run(state))
        p.step("Control Group", lambda: control_group.run(state, rivals, rival_pages))
        job.report = p.step("Report Writer", lambda: report_writer.run(state))  # type: ignore[assignment]
        job.status = "done" if job.report else "failed"
        if not job.report:
            job.error = "Report could not be generated"
    except Exception as exc:  # noqa: BLE001
        job.status, job.error = "failed", str(exc)
