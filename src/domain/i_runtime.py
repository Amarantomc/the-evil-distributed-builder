
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from api.job_status import JobSpec


@dataclass
class AttemptResult:
    # status: OK | TASK_FAILED | INFRA_FAILED | TIMEOUT
    status: str
    exit_code: Optional[int] = None
    output: str = ""
    node: Optional[str] = None
    duration_s: float = 0.0
    detail: str = ""


class Runtime(ABC):
    
    @abstractmethod
    def submit_attempt(self, attempt_id: str, spec: JobSpec) -> str:
         pass

    def poll(self, handle: str) -> Optional[AttemptResult]:
        pass