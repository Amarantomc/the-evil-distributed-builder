from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from typing import Dict, List

from api.job_status import JobSpec, JobStatus


@dataclass
class LogChunk:
    lines: List[str] = field(default_factory=list)
    next_offset: int = 0
    finished: bool = False

    def to_dict(self) -> Dict:
        return asdict(self)



class CiService(ABC):
    @abstractmethod
    def submit_job(self, spec: JobSpec) -> str:
        pass
    @abstractmethod
    def get_job(self, job_id: str) -> JobStatus:
        pass
    @abstractmethod
    def stream_logs(self, job_id: str, from_offset: int = 0) -> LogChunk:
        pass
    @abstractmethod
    def list_jobs(self) -> List[JobStatus]:
        pass