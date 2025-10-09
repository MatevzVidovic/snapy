

# import dill

# from functools import wraps
# from typing import Callable, TypeVar, ParamSpec, Any

# P = ParamSpec("P")
# R = TypeVar("R")

# def capture(recorder: Callable[[Callable[..., Any], tuple[Any, ...], dict[str, Any], Any], None]):
#     """Decorator factory that funnels call data to `recorder`."""
#     def decorator(func: Callable[P, R]) -> Callable[P, R]:
#         @wraps(func)
#         def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
#             result = func(*args, **kwargs)
#             recorder(func, args, kwargs, result)
#             return result
#         return wrapper
#     return decorator




from __future__ import annotations
import os, time
from functools import wraps
from pathlib import Path
from typing import Any, Callable, ParamSpec, TypeVar
import dill

"""
- CaptureHandler points at a base directory (captures/ or similar). Every call to record(...) stores one invocation of the wrapped function.
  - qualname = module.qualname turns nested names into a folder hierarchy (captures/examples/basics/RealOpsOne/expression/…), so each function gets its own bucket.
  - A millisecond timestamp becomes the filename ({ts}.pkl). The payload—a dict holding args, kwargs, result—is serialized with dill, so even complex objects survive.
  - index.json beside the blobs keeps metadata (timestamp, blob name). 
    Each new call appends to the index, sorts newest-first
  - Failures while pruning are swallowed to avoid breaking the hot path.

  End result: whenever the decorator wraps a function and SNAPY_CAPTURE=1, every invocation drops a dill-serialized snapshot of that call plus an updated index. You can
  later list captures, replay arguments, or diff results by reading the index and loading the *.pkl files.
"""


class CaptureHandler:
    def __init__(self, base_dir: str | Path) -> None:
        self.base_path = Path(base_dir)

    def get_target_dir(self, func: Callable[..., Any]) -> Path:
        qualname = f"{func.__module__}.{func.__qualname__}"
        target_dir = self.base_path / Path(*qualname.split("."))
        return target_dir
    
    def record(self, func: Callable[..., Any], args: tuple[Any, ...],
                kwargs: dict[str, Any], result: Any) -> None:

        target_dir = self.get_target_dir(func)
        target_dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time() * 1000)
        payload = {"args": args, "kwargs": kwargs, "result": result}
        blob_path = target_dir / f"{ts}.pkl"
        with blob_path.open("wb") as outf:
            dill.dump(payload, outf)
    
    def load_all(self, func: Callable[..., Any]) -> dict[str, Any] | None:

        target_dir = self.get_target_dir(func)
        if not target_dir.exists():
            return None
        blobs = list(target_dir.glob("*.pkl"))
        if not blobs:
            return None
        all_payloads = {}
        for blob_path in blobs:
            with blob_path.open("rb") as inf:
                payload = dill.load(inf)
                all_payloads[blob_path.name] = payload
        return all_payloads





P = ParamSpec("P")
R = TypeVar("R")

def capture(max_captures: int = 2,
            recorder: CaptureHandler = CaptureHandler("captures"),
            env_var: str = "SNAPY_CAPTURE") -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            result = func(*args, **kwargs)
            if os.getenv(env_var) == "1":
                try:
                    target_dir = recorder.get_target_dir(func)
                    num_of_files = len(list(target_dir.glob("*.pkl"))) if target_dir.exists() else 0
                    if num_of_files < max_captures:
                        recorder.record(func, args, kwargs, result)
                except Exception:
                    pass  # swallow capture errors in production paths
            return result
        return wrapper
    return decorator