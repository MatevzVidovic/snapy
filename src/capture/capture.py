from __future__ import annotations

import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Any, ParamSpec, TypeVar
from unittest.mock import MagicMock

import dill

"""
- capture snapshots under `captures/`
- bucket by module + qualname, name files by ms timestamp
- persist args/kwargs/result via dill; ignore capture errors in prod
"""


@dataclass
class CapturePayload:
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    result: Any


class CaptureHandler:
    @staticmethod
    def get_func_path_id(func: Callable[..., Any]) -> Path:
        """
        - purpose: stable folder ID of a given fn in the form of a path
        - how: use module name (e.g. src.capture.capture), join qualname (RealOps.plus)
        - example return: Path("src/capture/capture/RealOps.plus")
        """
        # - use declared module name (src.capture.capture)
        module_name = func.__module__
        if module_name == "__main__":
            # When fn is in `__main__`, .__module__ is __main__ instead of src.capture.capture.
            # - salvage this using import spec or file path
            module = sys.modules[module_name]
            spec = getattr(module, "__spec__", None)
            if spec and spec.name:
                module_name = spec.name
            else:
                file = getattr(module, "__file__", None)
                if file:
                    module_path = Path(file).resolve().with_suffix("").relative_to(Path.cwd())
                    module_name = ".".join(module_path.parts)

        # - map dotted module + qualname to nested path
        path_id = Path(*module_name.split(".")) / f"{func.__qualname__}"
        return path_id

    @staticmethod
    def get_target_path(func: Callable[..., Any], base_dir: str | Path = "captures") -> Path:
        """
        - purpose: locate capture folder
        - how: combine base dir with normalized function path
        """
        # - build path root + function path id
        base_path = Path(base_dir)
        target_dir = base_path / CaptureHandler.get_func_path_id(func)
        return target_dir

    @staticmethod
    def record(
        args: tuple[Any, ...], kwargs: dict[str, Any], result: Any, target_path: str | Path
    ) -> None:
        """
        - purpose: use dill to save special-snapshots (args, kwargs, return_value)
        """

        # - ensure capture folder exists
        target_path = Path(target_path)
        target_path.mkdir(parents=True, exist_ok=True)
        # - build payload blob
        ts = int(time.time() * 1000)
        payload = CapturePayload(args=args, kwargs=kwargs, result=result)
        blob_path = target_path / f"{ts}.pkl"
        with blob_path.open("wb") as outf:
            dill.dump(payload, outf)

    @staticmethod
    def get_blob_paths(target_path: str | Path) -> list[Path]:
        """
        - purpose: list stored special-snapshots
        - how: guard missing dirs, glob for `.pkl`
        """

        target_path = Path(target_path)
        if not target_path.exists():
            return []
        blobs = list(target_path.glob("*.pkl"))
        return blobs

    @staticmethod
    def get_blob(blob_path: str | Path) -> CapturePayload:
        """
        - purpose: load one snapshot
        - how: open binary path, dill.load
        """
        blob_path = Path(blob_path)
        with blob_path.open("rb") as inf:
            payload = dill.load(inf)
        assert isinstance(payload, CapturePayload)
        return payload


P = ParamSpec("P")
R = TypeVar("R")


def capture(
    max_captures: float = 2, target_path: str | Path | None = None, in_capture_mode: bool = True
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    - purpose: decorator capturing calls when env flag is set
    - how: wrap func; capture only if env var SNAPY_CAPTURE_ENABLED=1;
      if blob count limit reached, do not record more; delegate recording to handler
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # - execute wrapped function first
            result = func(*args, **kwargs)
            try:
                if in_capture_mode:
                    # - lazily resolve target folder
                    nonlocal target_path
                    target_path = (
                        CaptureHandler.get_target_path(func, "captures")
                        if target_path is None
                        else Path(target_path)
                    )
                    # - enforce capture limit
                    num_of_files = (
                        len(list(target_path.glob("*.pkl"))) if target_path.exists() else 0
                    )
                    if num_of_files < max_captures:
                        # - save current call special-snapshot
                        CaptureHandler.record(args, kwargs, result, target_path)
            except Exception:
                pass  # swallow capture errors for now
            return result

        return wrapper

    return decorator


# ---------- Side-effect capture section ----------
"""
Side-effect capture simply reuses regular arg capture mechanism - ctrl+F test_do_ops_DI_with_protocol_mock_snap in test_syrupy.py for how that is done and see the explanation.

Below are simply sugar-fns that make that use a lot cleaner.
"""


def side_effect_lookup(
    args: tuple[Any, ...],
    kwargs: dict[str, Any],
    target_path: str | Path,
    in_test_mode: bool = True,
) -> tuple[Any, bool]:
    """
    - return: (captured_return_val, was_found)
    - use: when making dependency injection mocks, we use @capture to store side-effect return val and fn args.
    We then use this function to load them up:
    this way we do not have to manually create mock return vals and fn args.
    - purpose: reuse stored outputs by arg match
    - how:  - scan existing blobs one by one,
            - if args+kwargs match, return cached result
            - if none matched, signal miss - caller will probably run the actual fn and capture it
    """
    blob_paths = CaptureHandler.get_blob_paths(target_path)
    # - look for payload matching provided args/kwargs
    existing_capture = None
    for bp in blob_paths:
        entry: CapturePayload = CaptureHandler.get_blob(bp)
        if entry.args == args and entry.kwargs == kwargs:
            existing_capture = entry
            break

    if existing_capture is not None:
        # - feed back cached result, was_found=True
        return existing_capture.result, True

    if in_test_mode:
        # - in test mode, missing capture is an error
        raise ValueError("No matching capture found and SIDE_EFFECT_CAPTURE is not set")
    return None, False


def side_effect_target_path(
    test_fn: Callable[..., Any],
    test_case_name: str,
    side_effect_mock: Callable[..., Any],
    storage_base_path: Path = Path("captures", "side_effect_capture"),
) -> Path:
    """
    - purpose: locate side-effect capture folder for test case
    - how: compose captures/side_effect_capture with function + mock + test name
    """
    return (
        storage_base_path
        / CaptureHandler.get_func_path_id(test_fn)
        / test_case_name
        / side_effect_mock.__qualname__
    )


def assert_side_effect_calls(
    test_fn: Callable[..., Any],
    test_case_name: str,
    side_effect_mock: Callable[..., Any],
    magic_mock: MagicMock,
) -> None:
    """
    - purpose: replay captured args against provided mock
    - how: load stored blobs and assert mock called with each payload
    """
    target_path = side_effect_target_path(test_fn, test_case_name, side_effect_mock)
    blobs = CaptureHandler.get_blob_paths(target_path)

    for bp in blobs:
        # - assert recorded call signature matches mock usage
        entry: CapturePayload = CaptureHandler.get_blob(bp)
        magic_mock.assert_called_with(*entry.args, **entry.kwargs)
