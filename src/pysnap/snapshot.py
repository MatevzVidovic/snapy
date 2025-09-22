"""
Snapshot integration for traced function calls.
"""

from typing import Any, List, Optional
from .tracer import FunctionTracer, CallEvent


class TracedSnapshot:
    """
    A snapshot class that captures function traces alongside return values.
    Integrates with Syrupy or can be used standalone.
    """
    
    def __init__(self, tracer: Optional[FunctionTracer] = None):
        """
        Initialize with an optional tracer instance.
        
        Args:
            tracer: FunctionTracer instance. If None, creates a new one.
        """
        self.tracer = tracer or FunctionTracer()
        self.traces: List[List[CallEvent]] = []
    
    def capture_trace(self, func: callable, *args, **kwargs) -> Any:
        """
        Execute a function while tracing and capture both trace and result.
        
        Args:
            func: Function to execute
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function
            
        Returns:
            The return value of the function
        """
        with self.tracer:
            result = func(*args, **kwargs)
            
        # Store the trace
        trace = self.tracer.get_trace()
        self.traces.append(trace)
        
        return result
    
    def format_trace_snapshot(self, include_result: bool = True) -> str:
        """
        Format the most recent trace as a snapshot string.
        
        Args:
            include_result: Whether to include the final result
            
        Returns:
            Formatted snapshot string
        """
        if not self.traces:
            return "No traces captured"
            
        latest_trace = self.traces[-1]
        return self._format_single_trace(latest_trace, include_result)
    
    def format_all_traces(self, include_results: bool = True) -> str:
        """
        Format all captured traces.
        
        Args:
            include_results: Whether to include final results
            
        Returns:
            Formatted string with all traces
        """
        if not self.traces:
            return "No traces captured"
            
        sections = []
        for i, trace in enumerate(self.traces):
            sections.append(f"=== Trace {i + 1} ===")
            sections.append(self._format_single_trace(trace, include_results))
            
        return "\n\n".join(sections)
    
    def _format_single_trace(self, trace: List[CallEvent], include_result: bool = True) -> str:
        """Format a single trace into a readable string."""
        if not trace:
            return "No function calls traced"
            
        lines = []
        call_stack = []
        final_result = None
        
        # Group calls and returns
        for event in trace:
            if event.event_type == 'call':
                indent = "  " * event.depth
                args_str = ", ".join(f"{k}={self._format_value(v)}" for k, v in event.args.items())
                
                # Determine the tree symbol
                if event.depth == 0:
                    symbol = "Function:"
                else:
                    symbol = "├─ Function:"
                    
                line = f"{indent}{symbol} {event.function_name}({args_str})"
                lines.append(line)
                call_stack.append(event)
                
            elif event.event_type == 'return':
                if call_stack:
                    call_event = call_stack.pop()
                    indent = "  " * event.depth
                    return_str = self._format_value(event.return_value)
                    
                    if event.depth == 0:
                        # This is the main function's return
                        final_result = event.return_value
                        if include_result:
                            line = f"{indent}└─ Returns: {return_str}"
                            lines.append(line)
                    else:
                        line = f"{indent}│  └─ Returns: {return_str}"
                        lines.append(line)
        
        result_text = "\n".join(lines)
        
        # Add final result summary if requested and available
        if include_result and final_result is not None:
            result_text += f"\n\nFinal Result: {self._format_value(final_result)}"
            
        return result_text
    
    def _format_value(self, value: Any) -> str:
        """Format a value for display in the snapshot."""
        if isinstance(value, str):
            return f"'{value}'"
        elif isinstance(value, (int, float, bool)):
            return str(value)
        elif value is None:
            return "None"
        elif isinstance(value, (list, tuple)):
            if len(value) <= 3:
                return repr(value)
            else:
                return f"[{len(value)} items]"
        elif isinstance(value, dict):
            if len(value) <= 3:
                return repr(value)
            else:
                return f"{{{len(value)} items}}"
        else:
            # For complex objects, use a simplified representation
            return f"<{type(value).__name__}>"
    
    def assert_match(self, snapshot_fixture, name: Optional[str] = None):
        """
        Assert that the trace matches the stored snapshot.
        Compatible with Syrupy's snapshot fixture.
        
        Args:
            snapshot_fixture: Syrupy snapshot fixture
            name: Optional name for the snapshot
        """
        trace_snapshot = self.format_trace_snapshot()
        
        if name:
            return snapshot_fixture(name=name) == trace_snapshot
        else:
            return snapshot_fixture == trace_snapshot
    
    def get_trace(self):
        """Get the most recent trace events."""
        if self.traces:
            return self.tracer.get_trace()
        return []
    
    def clear(self):
        """Clear all captured traces."""
        self.traces.clear()
        self.tracer.clear()


def create_traced_snapshot(filter_modules: Optional[List[str]] = None) -> TracedSnapshot:
    """
    Convenience function to create a TracedSnapshot with optional module filtering.
    
    Args:
        filter_modules: List of module name patterns to trace
        
    Returns:
        New TracedSnapshot instance
    """
    tracer = FunctionTracer(filter_modules=filter_modules)
    return TracedSnapshot(tracer)