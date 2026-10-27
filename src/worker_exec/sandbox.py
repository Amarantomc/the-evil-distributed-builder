"""Ejecuta un comando en un directorio temporal propio. Python puro, sin Ray.
"""


import os
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Optional

MAX_OUTPUT = 1_000_000  # bytes


@dataclass
class ExecResult:
    exit_code: int
    output: str
    timed_out: bool
    duration_s: float


def run_command(command: str, timeout_s: int, attempt_id: str,
                work_root: Optional[str] = None) -> ExecResult:
    work_root = work_root or os.environ.get("CI_WORK_ROOT", "/tmp/ci-work")
    os.makedirs(work_root, exist_ok=True)
    workdir = tempfile.mkdtemp(prefix=f"attempt-{attempt_id}-", dir=work_root)
    start = time.time()
    try:
        proc = subprocess.Popen(
            command, shell=True, cwd=workdir,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            start_new_session=True,  # para matar todo el grupo en timeout
        )
        try:
            out, _ = proc.communicate(timeout=timeout_s)
            timed_out = False
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            out, _ = proc.communicate()
            timed_out = True
        text = out[:MAX_OUTPUT].decode("utf-8", errors="replace")
        code = proc.returncode if not timed_out else -9
        return ExecResult(code, text, timed_out, time.time() - start)
    finally:
        if os.environ.get("CI_KEEP_WORKDIR") != "1":
            shutil.rmtree(workdir, ignore_errors=True)
