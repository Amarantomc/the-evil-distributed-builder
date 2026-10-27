
import ray

from api.job_status import JobSpec
from domain.job_manager import JobManager
from ray_runtime.ray_runtime import RayRuntime


@ray.remote(num_cpus=0)
class JobManagerActor:
    def __init__(self):
        self._jm = JobManager(RayRuntime())

    def submit(self, spec: dict) -> str:
        return self._jm.submit(JobSpec(**spec))

    def get(self, job_id: str) -> dict:
        return self._jm.get(job_id).to_dict()

    def logs(self, job_id: str, from_offset: int = 0) -> dict:
        return self._jm.logs(job_id, from_offset).to_dict()

    def list(self) -> list:
        return [s.to_dict() for s in self._jm.list()]