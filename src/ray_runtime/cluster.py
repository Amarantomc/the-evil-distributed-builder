

import os
import ray

from ray_runtime.ray_job_manager import JobManagerActor


NAMESPACE = "ci"
ACTOR_NAME = "job_manager"


def connect():
    if ray.is_initialized():
        return
    ray.init(address=os.environ.get("RAY_ADDRESS", "auto"),
             namespace=NAMESPACE, log_to_driver=False, logging_level="WARNING")


def get_manager():
    return JobManagerActor.options(
        name=ACTOR_NAME, namespace=NAMESPACE,
        get_if_exists=True, lifetime="detached").remote()