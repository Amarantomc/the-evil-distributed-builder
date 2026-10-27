
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Dict, Optional


class JobState(str, Enum):
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED_TASK = "FAILED_TASK"      
    FAILED_INFRA = "FAILED_INFRA"    
    CANCELLED = "CANCELLED"         


TERMINAL_STATES = {
    JobState.SUCCEEDED, JobState.FAILED_TASK, JobState.FAILED_INFRA, JobState.CANCELLED,
}


class FailureKind(str, Enum):
    NONE = "NONE"
    TASK = "TASK"
    INFRA = "INFRA"
    NETWORK = "NETWORK"   
    TIMEOUT = "TIMEOUT"


@dataclass
class JobSpec:
    command: str
    timeout_s: int = 60
    client_request_id: Optional[str] = None  # para envios idempotentes


@dataclass
class JobStatus:
    job_id: str
    state: JobState
    command: str
    failure_kind: FailureKind = FailureKind.NONE
    exit_code: Optional[int] = None
    node: Optional[str] = None
    attempts: int = 1
    submitted_at: float = 0.0
    finished_at: Optional[float] = None
    detail: str = ""

    def to_dict(self) -> Dict:
        d = asdict(self)
        d["state"] = self.state.value
        d["failure_kind"] = self.failure_kind.value
        return d