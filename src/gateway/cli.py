"""CLI del cliente.  Uso:  python -m ci.gateway.cli <comando> ...

"""

import argparse
import json
import sys
import time

from api.job_status import JobNotFound, JobSpec
from gateway.ray_gateway import RayGateway


def _print(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))


def _follow(gw, job_id, offset=0, poll_s=0.5):
    while True:
        chunk = gw.stream_logs(job_id, offset)
        for line in chunk.lines:
            print(line)
        offset = chunk.next_offset
        if chunk.finished:
            return
        time.sleep(poll_s)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ci")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("submit")
    s.add_argument("command")
    s.add_argument("--timeout", type=int, default=60)
    s.add_argument("--request-id", default=None)
    s.add_argument("--wait", action="store_true")

    st = sub.add_parser("status")
    st.add_argument("job_id")
    lg = sub.add_parser("logs")
    lg.add_argument("job_id")
    lg.add_argument("--from", dest="offset", type=int, default=0)
    lg.add_argument("--follow", action="store_true")
    sub.add_parser("list")
    pg = sub.add_parser("ping")
    pg.add_argument("--n", type=int, default=6)
    return p


def main(argv=None) -> int:
    a = build_parser().parse_args(argv)

    
    gw = RayGateway()
    try:
        if a.cmd == "submit":
            job_id = gw.submit_job(JobSpec(a.command, a.timeout, a.request_id))
            print(job_id)
            if a.wait:
                _follow(gw, job_id)
                status = gw.get_job(job_id)
                _print(status.to_dict())
                return 0 if status.state.value == "SUCCEEDED" else 1
        elif a.cmd == "status":
            _print(gw.get_job(a.job_id).to_dict())
        elif a.cmd == "logs":
            if a.follow:
                _follow(gw, a.job_id, a.offset)
            else:
                chunk = gw.stream_logs(a.job_id, a.offset)
                print("\n".join(chunk.lines))
                print(f"-- next_offset={chunk.next_offset} finished={chunk.finished}",
                      file=sys.stderr)
        elif a.cmd == "list":
            _print([j.to_dict() for j in gw.list_jobs()])
        elif a.cmd == "ping":
            _print(gw.ping(a.n))
    except JobNotFound as e:
        print(f"job no encontrado: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
