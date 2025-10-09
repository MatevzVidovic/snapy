

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

    
    @staticmethod
    def get_func_path_id(func: Callable[..., Any]) -> Path:
        qualname = f"{func.__module__}.{func.__qualname__}"
        path_id = Path(*qualname.split("."))
        return path_id

    @staticmethod
    def get_target_path(func: Callable[..., Any], base_dir: str | Path = "captures") -> Path:
        base_path = Path(base_dir)
        target_dir = base_path / CaptureHandler.get_func_path_id(func)
        return target_dir
    
    @staticmethod
    def record(args: tuple[Any, ...],
                kwargs: dict[str, Any], result: Any, target_path: str | Path) -> None:

        target_path.mkdir(parents=True, exist_ok=True)
        ts = int(time.time() * 1000)
        payload = {"args": args, "kwargs": kwargs, "result": result}
        blob_path = target_path / f"{ts}.pkl"
        with blob_path.open("wb") as outf:
            dill.dump(payload, outf)
    
    @staticmethod
    def get_blob_paths(target_path: str | Path) -> dict[str, Any] | None:

        target_path = Path(target_path)
        if not target_path.exists():
            return None
        blobs = list(target_path.glob("*.pkl"))
        if not blobs:
            return None
        return blobs
    
    @staticmethod
    def get_blob(blob_path: str | Path) -> dict[str, Any] | None:
        with blob_path.open("rb") as inf:
            payload = dill.load(inf)
        return payload

    @staticmethod
    def load_all(target_path: str | Path | Callable[..., Any]) -> dict[str, Any] | None:
        if callable(target_path):
            target_path = CaptureHandler.get_target_path(target_path)
        blobs = CaptureHandler.get_blob_paths(target_path)
        if blobs is None:
            return {}
        
        all_payloads = {}
        for blob_path in blobs:
            all_payloads[blob_path.name] = CaptureHandler.get_blob(blob_path)
        return all_payloads





P = ParamSpec("P")
R = TypeVar("R")

def capture(max_captures: float = 2,
            env_var: str = "SNAPY_CAPTURE", target_path: str | Path = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:

            result = func(*args, **kwargs)
            if os.getenv(env_var) == "1":
                try:
                    nonlocal target_path
                    target_path = CaptureHandler.get_target_path(func, "captures") if target_path is None else target_path
                    num_of_files = len(list(target_path.glob("*.pkl"))) if target_path.exists() else 0
                    if num_of_files < max_captures:
                        CaptureHandler.record(args, kwargs, result, target_path)
                except Exception:
                    pass  # swallow capture errors in production paths
            return result
        return wrapper
    return decorator



def side_effect_lookup(args: tuple[Any, ...], kwargs: dict[str, Any], target_path: str | Path) -> tuple[Any, bool]:
    blob_paths = CaptureHandler.get_blob_paths(target_path) or []
    existing_capture = None
    for bp in blob_paths:
        entry = CaptureHandler.get_blob(bp)
        if entry["args"] == args and entry["kwargs"] == kwargs:
            existing_capture = entry
            break
    
    if existing_capture is not None:
        return existing_capture["result"], True
    
    if not os.getenv("SIDE_EFFECT_CAPTURE") == "1":
        raise ValueError("No matching capture found and SIDE_EFFECT_CAPTURE is not set")
    return None, False

def side_effect_target_path(test_fn: Callable[..., Any], side_effect_mock: Callable[..., Any], test_case_name: str) -> Path:
    return Path("captures", "side_effect_capture") / CaptureHandler.get_func_path_id(test_fn) \
          / side_effect_mock.__qualname__ / test_case_name


def assert_side_effect_calls(test_fn: Callable[..., Any], side_effect_mock: Callable[..., Any], test_case_name: str, magic_mock: Callable[..., Any]) -> None:
    target_path = side_effect_target_path(test_fn, side_effect_mock, test_case_name)
    blobs = CaptureHandler.get_blob_paths(target_path) or []

    for bp in blobs:
        entry = CaptureHandler.get_blob(bp)
        magic_mock.assert_called_with(*entry["args"], **entry["kwargs"])
