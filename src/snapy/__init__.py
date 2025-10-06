"""
Snapy - Python Testing Framework with Argument Capture and Function Tracing

A powerful extension to snapshot testing that captures function arguments,
return values, and nested function calls for comprehensive test validation.
"""

from .capture import capture_args, load_capture, load_capture_dict, CaptureConfig
from .testing import FunctionTracer, CallEvent, TracedSnapshot

__version__ = "2.0.0"
__all__ = [
    # Capture functionality
    "capture_args",
    "load_capture",
    "load_capture_dict",
    "CaptureConfig",

    # Testing functionality
    "FunctionTracer",
    "CallEvent",
    "TracedSnapshot"
]