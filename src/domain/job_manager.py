
from dataclasses import dataclass
import time
from typing import Dict, List, Optional
import uuid

from api.ci_service import LogChunk
from api.job_status import TERMINAL_STATES, FailureKind, JobNotFound, JobSpec, JobState, JobStatus
from domain.i_runtime import AttemptResult, Runtime


@dataclass
class _Record:
    spec: JobSpec
    status: JobStatus
    handle: str
    output: str = ""


_STATUS_MAP = {
    "OK": (JobState.SUCCEEDED, FailureKind.NONE),
    "TASK_FAILED": (JobState.FAILED_TASK, FailureKind.TASK),
    "TIMEOUT": (JobState.FAILED_TASK, FailureKind.TIMEOUT),
    "INFRA_FAILED": (JobState.FAILED_INFRA, FailureKind.INFRA),
}


class JobManager:
    def __init__(self, runtime: Runtime):
        self._rt = runtime
        self._jobs: Dict[str, _Record] = {}
        self._by_request: Dict[str, str] = {}

    def submit(self, spec: JobSpec) -> str:
        # Idempotencia: mismo client_request_id -> mismo job_id
        if spec.client_request_id and spec.client_request_id in self._by_request:
            return self._by_request[spec.client_request_id]
        job_id = uuid.uuid4().hex[:8]
        attempt_id = f"{job_id}-a1"
        handle = self._rt.submit_attempt(attempt_id, spec)
        status = JobStatus(job_id=job_id, state=JobState.RUNNING,
                           command=spec.command, submitted_at=time.time())
        self._jobs[job_id] = _Record(spec, status, handle)
        if spec.client_request_id:
            self._by_request[spec.client_request_id] = job_id
        return job_id

    def _refresh(self, rec: _Record) -> None:
        if rec.status.state in TERMINAL_STATES:
            return
        res: Optional[AttemptResult] = self._rt.poll(rec.handle)
        if res is None:
            return
        state, kind = _STATUS_MAP.get(res.status, (JobState.FAILED_INFRA, FailureKind.INFRA))
        rec.status.state = state
        rec.status.failure_kind = kind
        rec.status.exit_code = res.exit_code
        rec.status.node = res.node
        rec.status.detail = res.detail
        rec.status.finished_at = time.time()
        rec.output = res.output

    def _get(self, job_id: str) -> _Record:
        rec = self._jobs.get(job_id)
        if rec is None:
            raise JobNotFound(job_id)
        self._refresh(rec)
        return rec

    def get(self, job_id: str) -> JobStatus:
        return self._get(job_id).status

    def logs(self, job_id: str, from_offset: int = 0) -> LogChunk:
        rec = self._get(job_id)
        lines = rec.output.splitlines()
        finished = rec.status.state in TERMINAL_STATES
        return LogChunk(lines=lines[from_offset:], next_offset=len(lines), finished=finished)

    def list(self) -> List[JobStatus]:
        return [self.get(j) for j in self._jobs]