"""Orchestrates the seven agents over one shared AuditState and reports progress."""
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor

from app.agents import (
    benchmark, content_survival, control_group, crawl_access, fetcher, hidden_scan, interrogator, missing_facts, query_discovery, question_miner, report_writer, skeptic, structured_data, visitor,
)
from app.schemas.api import AuditJob

AGENTS = ["Fetcher", "Visitor", "Crawl Access", "Structured Data", "Missing-Facts", "Content Survival",
          "Hidden Scan", "Query Discovery", "Question Miner", "Interrogator", "Skeptic", "Benchmark",
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
        with ThreadPoolExecutor(max_workers=4) as pool:  # independent agents run in parallel
            futures = [pool.submit(p.step, "Fetcher", lambda: fetcher.run(state)),
                       pool.submit(p.step, "Visitor", lambda: visitor.run(state)),
                       pool.submit(p.step, "Crawl Access", lambda: crawl_access.run(state)),
                       pool.submit(p.step, "Structured Data", lambda: structured_data.run(state))]
            for f in futures:
                f.result()
        p.step("Missing-Facts", lambda: missing_facts.run(state))
        p.step("Content Survival", lambda: content_survival.run(state))
        p.step("Hidden Scan", lambda: hidden_scan.run(state))
        p.step("Query Discovery", lambda: query_discovery.run(state))
        rival_pages: dict[str, str] = {}
        rivals = p.step("Question Miner", lambda: question_miner.run(state, rival_pages)) or []
        p.step("Interrogator", lambda: interrogator.run(state))
        p.step("Skeptic", lambda: skeptic.run(state))
        p.step("Benchmark", lambda: benchmark.run(state, rival_pages))
        p.step("Control Group", lambda: control_group.run(state, rivals, rival_pages))
        job.report = p.step("Report Writer", lambda: report_writer.run(state))  # type: ignore[assignment]
        if not job.report:  # last resort: minimal report from whatever evidence exists
            from app.schemas.api import Report
            job.report = Report(verdict="Partial audit: some agents failed. Showing the evidence collected.")
        job.status = "done"
    except Exception as exc:  # noqa: BLE001
        job.status, job.error = "failed", str(exc)
