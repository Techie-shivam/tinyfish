import uuid

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import PlainTextResponse

from app.agents import report_writer
from app.schemas.api import AgentProgress, AuditJob, AuditRequest
from app.schemas.state import AuditState
from app.schemas.state import Verification
from app.services.pipeline import AGENTS, run_audit
from app.services.verify import verify

router = APIRouter(prefix="/api")
JOBS: dict[str, AuditJob] = {}  # in-memory store; audits are live and never cached


@router.post("/audits", response_model=AuditJob, status_code=202)
def create_audit(req: AuditRequest, background: BackgroundTasks) -> AuditJob:
    job = AuditJob(
        id=uuid.uuid4().hex[:12],
        agents=[AgentProgress(name=n) for n in AGENTS],
        state=AuditState(url=str(req.url), target_query=req.target_query.strip()),
    )
    JOBS[job.id] = job
    background.add_task(run_audit, job)
    return job


def _get(job_id: str) -> AuditJob:
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(404, "Audit not found")
    return job


@router.get("/audits/{job_id}", response_model=AuditJob)
def get_audit(job_id: str) -> AuditJob:
    return _get(job_id)


@router.get("/audits/{job_id}/report.md", response_class=PlainTextResponse)
def get_markdown(job_id: str) -> str:
    job = _get(job_id)
    if not job.report:
        raise HTTPException(409, "Report not ready")
    return report_writer.to_markdown(job.state, job.report)


@router.post("/audits/{job_id}/verify", response_model=Verification)
def verify_fixes(job_id: str) -> Verification:
    job = _get(job_id)
    if job.status != "done":
        raise HTTPException(409, "Audit not finished")
    return verify(job.state)
