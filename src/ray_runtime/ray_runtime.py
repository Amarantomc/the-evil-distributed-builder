
import os
from typing import Dict, Optional
from api.job_status import JobSpec
from domain.i_runtime import AttemptResult, Runtime
import ray
from ray_runtime import run_attempt
from ray_runtime.error_mapping import map_exception

class RayRuntime (Runtime):
    def __init__(self):
        self._refs: Dict[str, "ray.ObjectRef"] = {}
        self._max_retries = int(os.environ.get("CI_RAY_MAX_RETRIES", "0"))

    def submit_attempt(self, attempt_id: str, spec: JobSpec) -> str:
        ref = run_attempt.options(num_cpus=1, max_retries=self._max_retries).remote(
            spec.command, spec.timeout_s, attempt_id)
        self._refs[attempt_id] = ref
        return attempt_id

    def poll(self, handle: str) -> Optional[AttemptResult]:
        ref = self._refs[handle]
        ready, _ = ray.wait([ref], timeout=0)
        if not ready:
            return None
        try:
            return AttemptResult(**ray.get(ref))
        except Exception as exc:  # noqa: BLE001
            return map_exception(exc)
