"""
PySnap - Enhanced Snapshot Testing with Function Tracing

A powerful extension to snapshot testing that captures function arguments,
return values, and nested function calls for comprehensive test validation.
"""

from .tracer import FunctionTracer, CallEvent
from .snapshot import TracedSnapshot
from .decorators import trace_snapshot, trace_module, quick_trace
from .context import trace_calls

__version__ = "0.1.0"
__all__ = [
    "FunctionTracer",
    "CallEvent", 
    "TracedSnapshot",
    "trace_snapshot",
    "trace_module",
    "trace_calls",
    "quick_trace"
]