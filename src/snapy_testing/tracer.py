"""
Core function tracing functionality using sys.settrace.
"""

import sys
import threading
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Callable, Union
from types import FrameType


@dataclass
class CallEvent:
    """Represents a single function call event."""
    event_type: str  # 'call' or 'return'
    function_name: str
    filename: str
    line_number: int
    args: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    depth: int = 0
    timestamp: float = 0.0


class FunctionTracer:
    """
    Traces function calls and returns using sys.settrace.
    Captures arguments, return values, and nested function calls.
    """
    
    def __init__(self, filter_modules: Optional[List[str]] = None):
        """
        Initialize the tracer.
        
        Args:
            filter_modules: List of module name patterns to trace. 
                          If None, traces all modules except system modules.
        """
        self.filter_modules = filter_modules or []
        self.events: List[CallEvent] = []
        self.call_stack: List[CallEvent] = []
        self.original_trace = None
        self.is_tracing = False
        self.thread_local = threading.local()
        
    def should_trace_frame(self, frame: FrameType) -> bool:
        """Determine if we should trace this frame."""
        filename = frame.f_code.co_filename
        function_name = frame.f_code.co_name
        
        # Skip system modules and built-ins
        if ('<' in filename and '>' in filename) or 'site-packages' in filename:
            return False
            
        # Skip special methods unless explicitly wanted
        if function_name.startswith('__') and function_name.endswith('__'):
            return False
            
        # If filter_modules specified, only trace those
        if self.filter_modules:
            return any(module in filename for module in self.filter_modules)
            
        # Default: trace non-system files
        return not any(skip in filename for skip in ['/usr/lib', '/usr/local/lib', 'site-packages'])
    
    def extract_args(self, frame: FrameType) -> Dict[str, Any]:
        """Extract function arguments from frame."""
        code = frame.f_code
        args = {}
        
        # Get argument names
        arg_names = code.co_varnames[:code.co_argcount]
        
        # Extract values
        for i, name in enumerate(arg_names):
            if name in frame.f_locals:
                args[name] = frame.f_locals[name]
                
        return args
    
    def trace_function(self, frame: FrameType, event: str, arg: Any) -> Optional[Callable]:
        """The trace function called by sys.settrace."""
        if not self.should_trace_frame(frame):
            return self.trace_function
            
        import time
        
        function_name = frame.f_code.co_name
        filename = frame.f_code.co_filename
        line_number = frame.f_lineno
        depth = len(self.call_stack)
        
        if event == 'call':
            # Function is being called
            args = self.extract_args(frame)
            
            call_event = CallEvent(
                event_type='call',
                function_name=function_name,
                filename=filename,
                line_number=line_number,
                args=args,
                depth=depth,
                timestamp=time.time()
            )
            
            self.events.append(call_event)
            self.call_stack.append(call_event)
            
        elif event == 'return':
            # Function is returning
            if self.call_stack:
                call_event = self.call_stack.pop()
                
                return_event = CallEvent(
                    event_type='return',
                    function_name=function_name,
                    filename=filename,
                    line_number=line_number,
                    return_value=arg,
                    depth=depth - 1,
                    timestamp=time.time()
                )
                
                self.events.append(return_event)
                
        return self.trace_function
    
    def start_tracing(self):
        """Start tracing function calls."""
        if not self.is_tracing:
            self.original_trace = sys.gettrace()
            sys.settrace(self.trace_function)
            self.is_tracing = True
            self.events.clear()
            self.call_stack.clear()
    
    def stop_tracing(self):
        """Stop tracing function calls."""
        if self.is_tracing:
            sys.settrace(self.original_trace)
            self.is_tracing = False
    
    def get_trace(self) -> List[CallEvent]:
        """Get the collected trace events."""
        return self.events.copy()
    
    def clear(self):
        """Clear all collected events."""
        self.events.clear()
        self.call_stack.clear()
    
    def format_trace(self, show_returns: bool = True) -> str:
        """
        Format the trace as a readable string.
        
        Args:
            show_returns: Whether to show return values in the output.
        """
        lines = []
        call_stack = []
        
        for event in self.events:
            if event.event_type == 'call':
                indent = "  " * event.depth
                args_str = ", ".join(f"{k}={repr(v)}" for k, v in event.args.items())
                line = f"{indent}├─ Function: {event.function_name}({args_str})"
                lines.append(line)
                call_stack.append(event)
                
            elif event.event_type == 'return' and show_returns:
                if call_stack:
                    call_event = call_stack.pop()
                    indent = "  " * event.depth
                    return_str = repr(event.return_value)
                    line = f"{indent}│  └─ Returns: {return_str}"
                    lines.append(line)
        
        return "\n".join(lines)
    
    def __enter__(self):
        """Context manager entry."""
        self.start_tracing()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_tracing()
        return False