"""Traduce excepciones de Ray a AttemptResult (clasificacion de fallos)."""
from domain.i_runtime import AttemptResult
import ray.exceptions as rx

_INFRA_NAMES = ("WorkerCrashedError", "NodeDiedError", "OutOfMemoryError",
                "RayActorError", "ObjectLostError", "RaySystemError")
_INFRA_TYPES = tuple(getattr(rx, n) for n in _INFRA_NAMES if hasattr(rx, n))


def map_exception(exc: BaseException) -> AttemptResult:
    if isinstance(exc, _INFRA_TYPES):
        return AttemptResult(status="INFRA_FAILED", detail=f"{type(exc).__name__}: {exc}")
    # RayTaskError = excepcion dentro de NUESTRO codigo (el comando ya lo
    # captura el sandbox), asi que aqui es un bug de la app: lo tratamos como infra.
    return AttemptResult(status="INFRA_FAILED",
                         detail=f"unexpected {type(exc).__name__}: {exc}")
