import ray
import os
import socket

from worker_exec.sandbox import run_command
@ray.remote
def run_attempt(command: str, timeout_s: int, attempt_id: str) -> dict:
    res = run_command(command, timeout_s, attempt_id)
    if res.timed_out:
        status = "TIMEOUT"
    elif res.exit_code == 0:
        status = "OK"
    else:
        status = "TASK_FAILED"
    return {
        "status": status,
        "exit_code": res.exit_code,
        "output": res.output,
        "node": os.environ.get("NODE_NAME", socket.gethostname()),
        "duration_s": res.duration_s,
    }


@ray.remote
def whoami(sleep_s: float = 1.0) -> str:
    """Tarea trivial para probar que Ray reparte trabajo entre nodos."""
    import time
    time.sleep(sleep_s)
    return os.environ.get("NODE_NAME", socket.gethostname())