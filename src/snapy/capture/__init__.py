"""
Snapy Capture - Automatic Function Argument Capture for Replay Testing

A decorator-based system for capturing function arguments and enabling easy
replay in snapshot tests without manually creating test arguments.
"""

from .config import CaptureConfig
from .storage import CaptureStorage
from .filters import ArgumentFilter
from .capture import capture_args
from .loader import CaptureLoader, load_capture, load_capture_dict, has_capture

__version__ = "0.1.0"
__all__ = [
    "capture_args",
    "CaptureConfig",
    "CaptureStorage",
    "ArgumentFilter",
    "CaptureLoader",
    "load_capture",
    "load_capture_dict",
    "has_capture"
]