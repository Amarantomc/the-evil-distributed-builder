from collections import Counter
from dataclasses import asdict
from typing import List

import ray

from api.ci_service import CiService, LogChunk
from api.job_status import FailureKind, JobNotFound, JobSpec, JobState, JobStatus
from ray_runtime import cluster
from ray_runtime.executor import whoami



def _to_status(d: dict) -> JobStatus:
    d = dict(d)
    d["state"] = JobState(d["state"])
    d["failure_kind"] = FailureKind(d["failure_kind"])
    return JobStatus(**d)


def _unwrap_not_found(e: ray.exceptions.RayTaskError, job_id: str):
    if isinstance(e.cause, JobNotFound):
        raise JobNotFound(job_id) from None
    raise e


class RayGateway(CiService):
    def __init__(self):
        cluster.connect()
        self._mgr = cluster.get_manager()

    def submit_job(self, spec: JobSpec) -> str:
        return ray.get(self._mgr.submit.remote(asdict(spec)))

    def get_job(self, job_id: str) -> JobStatus:
        try:
            return _to_status(ray.get(self._mgr.get.remote(job_id)))
        except ray.exceptions.RayTaskError as e:
            _unwrap_not_found(e, job_id)

    def stream_logs(self, job_id: str, from_offset: int = 0) -> LogChunk:
        try:
            return LogChunk(**ray.get(self._mgr.logs.remote(job_id, from_offset)))
        except ray.exceptions.RayTaskError as e:
            _unwrap_not_found(e, job_id)

    def list_jobs(self) -> List[JobStatus]:
        return [_to_status(d) for d in ray.get(self._mgr.list.remote())]

    # --- utilidad de diagnostico (no es parte del contrato) ---
    def ping(self, n: int = 6, sleep_s: float = 1.0) -> dict:
        nodes = [{"node_id": x["NodeID"][:8], "alive": x["Alive"],
                  "resources": x["Resources"]} for x in ray.nodes()]
        hosts = ray.get([whoami.remote(sleep_s) for _ in range(n)])
        return {"nodes": nodes, "task_distribution": dict(Counter(hosts))}
