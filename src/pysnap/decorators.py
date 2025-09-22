"""
Decorator API for easy function tracing.
"""

import functools
from typing import Callable, Any, Optional, List
from .tracer import FunctionTracer
from .snapshot import TracedSnapshot


def trace_snapshot(
    filter_modules: Optional[List[str]] = None,
    capture_args: bool = True,
    capture_returns: bool = True
):
    """
    Decorator that automatically traces a function and its nested calls.
    
    Args:
        filter_modules: List of module patterns to trace. If None, traces all non-system modules.
        capture_args: Whether to capture function arguments
        capture_returns: Whether to capture return values
    
    Returns:
        Decorated function that traces all calls when executed
    
    Example:
        @trace_snapshot()
        def my_function(arg1, arg2):
            return helper_function(arg1) + arg2
            
        # When called, traces my_function and helper_function
        result = my_function("hello", "world")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a tracer for this execution
            tracer = FunctionTracer(filter_modules=filter_modules)
            
            # Execute with tracing
            with tracer:
                result = func(*args, **kwargs)
            
            # Store trace on the function for later access
            wrapper._last_trace = tracer.get_trace()
            wrapper._last_formatted = tracer.format_trace(show_returns=capture_returns)
            
            return result
        
        # Add methods to access trace data
        def get_last_trace():
            """Get the trace from the last function call."""
            return getattr(wrapper, '_last_trace', [])
        
        def get_last_formatted():
            """Get the formatted trace from the last function call."""
            return getattr(wrapper, '_last_formatted', 'No trace available')
        
        def clear_trace():
            """Clear stored trace data."""
            wrapper._last_trace = []
            wrapper._last_formatted = 'No trace available'
        
        wrapper.get_last_trace = get_last_trace
        wrapper.get_last_formatted = get_last_formatted
        wrapper.clear_trace = clear_trace
        
        return wrapper
    
    return decorator


def trace_module(
    module_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None
):
    """
    Class decorator that traces all methods in a class/module.
    
    Args:
        module_patterns: Module patterns to include in tracing
        exclude_patterns: Module patterns to exclude from tracing
        
    Example:
        @trace_module()
        class MyClass:
            def method1(self):
                return self.method2()
                
            def method2(self):
                return "result"
    """
    def decorator(cls):
        # Store original methods
        original_methods = {}
        
        # Wrap each method
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and not attr_name.startswith('_'):
                original_methods[attr_name] = attr
                
                # Create traced version
                traced_method = trace_snapshot(
                    filter_modules=module_patterns
                )(attr)
                
                setattr(cls, attr_name, traced_method)
        
        # Add methods to access all traces
        def get_all_traces(self):
            """Get traces from all methods."""
            traces = {}
            for method_name in original_methods:
                method = getattr(self, method_name)
                if hasattr(method, 'get_last_trace'):
                    traces[method_name] = method.get_last_trace()
            return traces
        
        def get_all_formatted(self):
            """Get formatted traces from all methods."""
            formatted = {}
            for method_name in original_methods:
                method = getattr(self, method_name)
                if hasattr(method, 'get_last_formatted'):
                    formatted[method_name] = method.get_last_formatted()
            return formatted
        
        cls.get_all_traces = get_all_traces
        cls.get_all_formatted = get_all_formatted
        
        return cls
    
    return decorator


class TraceCollector:
    """
    A utility class for collecting traces from multiple decorated functions.
    Useful for test scenarios where you want to examine traces from several calls.
    """
    
    def __init__(self):
        self.collected_traces = []
        self.collected_formatted = []
    
    def collect_from_function(self, func: Callable):
        """
        Collect trace from a decorated function.
        
        Args:
            func: Function decorated with @trace_snapshot
        """
        if hasattr(func, 'get_last_trace'):
            trace = func.get_last_trace()
            formatted = func.get_last_formatted()
            
            self.collected_traces.append({
                'function': func.__name__,
                'trace': trace,
                'formatted': formatted
            })
    
    def get_combined_formatted(self) -> str:
        """Get all collected traces as a single formatted string."""
        if not self.collected_traces:
            return "No traces collected"
        
        sections = []
        for i, entry in enumerate(self.collected_traces):
            sections.append(f"=== {entry['function']} ===")
            sections.append(entry['formatted'])
        
        return "\n\n".join(sections)
    
    def clear(self):
        """Clear all collected traces."""
        self.collected_traces.clear()
        self.collected_formatted.clear()


# Convenience function for quick testing
def quick_trace(func: Callable, *args, **kwargs) -> tuple:
    """
    Quickly trace a function call and return both result and formatted trace.
    
    Args:
        func: Function to trace
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
    
    Returns:
        Tuple of (result, formatted_trace)
    
    Example:
        result, trace = quick_trace(my_function, "arg1", "arg2")
        print(trace)
    """
    tracer = FunctionTracer()
    
    with tracer:
        result = func(*args, **kwargs)
    
    formatted = tracer.format_trace()
    return result, formatted