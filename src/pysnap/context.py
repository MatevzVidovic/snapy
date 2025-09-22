"""
Context manager API for tracing code blocks without modifying functions.


TL;DR

Don't use this yet.

Only maybe:
  with trace_calls() as tracer:
      result = complex_function(data)
  print(tracer.get_formatted_trace())

  # Production debugging (conditional)
  if os.getenv('DEBUG_MODE'):
      with trace_calls(filter_modules=['myapp']) as tracer:
          process_user_request(request)
          logger.debug(tracer.get_formatted_trace())






How and When to Use Each context.py Function

  1. trace_calls() - Most Common Usage

  When: Debugging, development, conditional tracing
  # Basic debugging
  with trace_calls() as tracer:
      result = complex_function(data)
  print(tracer.get_formatted_trace())

  # Production debugging (conditional)
  if os.getenv('DEBUG_MODE'):
      with trace_calls(filter_modules=['myapp']) as tracer:
          process_user_request(request)
          logger.debug(tracer.get_formatted_trace())

  # Development workflow
  with trace_calls() as tracer:
      bug_reproduction_scenario()
      # Analyze what functions were called and with what args

  2. trace_execution() - One-Shot Function Analysis

  When: You want to trace one specific function call and get everything in one go
  # Quick function analysis
  with trace_execution(problematic_function, user_data, config) as exec_data:
      pass

  print(f"Function returned: {exec_data['result']}")
  print(f"Call tree:\n{exec_data['trace']}")

  # Unit test debugging
  def test_my_function():
      with trace_execution(my_function, test_input) as exec_data:
          pass

      assert exec_data['result'] == expected
      # If test fails, inspect exec_data['trace'] to see what happened

  3. TraceSession - Complex Debugging Sessions

  When: You need to analyze multiple related function calls with organization
  # Complex debugging session
  session = TraceSession("User Registration Flow")

  # Trace validation step
  with session.start_context("validation", filter_modules=['myapp.validation']) as ctx:
      validation_result = validate_user_data(user_input)
  session.save_current_trace("user_validation")

  # Trace database step
  with session.start_context("database", filter_modules=['myapp.db']) as ctx:
      user_id = create_user_record(validated_data)
  session.save_current_trace("db_creation")

  # Trace notification step
  with session.start_context("notifications", filter_modules=['myapp.notify']) as ctx:
      send_welcome_email(user_id)
  session.save_current_trace("email_sending")

  # Analyze entire workflow
  print(session.get_session_summary())

  4. trace_function_call() - Quick One-Liners

  When: You need a quick trace without context manager setup
  # Quick debugging in REPL/notebook
  result, trace = trace_function_call(suspicious_function, problematic_input)
  print("Result:", result)
  print("Trace:", trace)

  # Testing different inputs quickly
  for test_input in test_cases:
      result, trace = trace_function_call(my_function, test_input)
      if "error" in trace.lower():
          print(f"Problem with input {test_input}:")
          print(trace)

  5. compare_traces() - A/B Function Analysis

  When: Comparing different implementations or debugging differences
  # Compare old vs new implementation
  comparison = compare_traces(
      (old_algorithm, (data,), {}),
      (new_algorithm, (data,), {}),
      (optimized_algorithm, (data,), {})
  )
  print(comparison)

  # Debug why two similar calls behave differently
  comparison = compare_traces(
      (process_request, (good_request,), {}),
      (process_request, (bad_request,), {})
  )
  # See exactly where the execution paths diverge

  Real-World Usage Patterns:

  Production Debugging:
  # Enable tracing via environment variable
  if os.getenv('TRACE_REQUESTS'):
      with trace_calls(filter_modules=['myapp']) as tracer:
          handle_api_request(request)
          if response.status_code >= 400:
              logger.error(f"Request failed. Trace: {tracer.get_formatted_trace()}")

  Test Development:
  def test_complex_workflow():
      session = TraceSession("Integration Test")

      with session.start_context("setup") as ctx:
          setup_test_data()
      session.save_current_trace()

      with session.start_context("main_flow") as ctx:
          result = main_workflow(test_data)
      session.save_current_trace()

      # If test fails, session.get_session_summary() shows exactly what happened

  Performance Analysis:
  # See which functions are called most in different scenarios
  light_load_result, light_trace = trace_function_call(process_data, small_dataset)
  heavy_load_result, heavy_trace = trace_function_call(process_data, large_dataset)

  # Compare call patterns to identify bottlenecks
"""

from typing import Optional, List, Any, Callable
from contextlib import contextmanager
from .tracer import FunctionTracer, CallEvent
from .snapshot import TracedSnapshot


class TracingContext:
    """
    Context manager for tracing function calls within a code block.
    No function modification required - just wrap the code you want to trace.
    """
    
    def __init__(
        self, 
        filter_modules: Optional[List[str]] = None,
        capture_all: bool = False,
        name: Optional[str] = None
    ):
        """
        Initialize the tracing context.
        
        Args:
            filter_modules: List of module patterns to trace. If None, uses intelligent filtering.
            capture_all: If True, captures all function calls including system calls.
            name: Optional name for this tracing session.
        """
        self.filter_modules = filter_modules
        self.capture_all = capture_all
        self.name = name or "TracingContext"
        self.tracer = None
        self.result = None
    
    def __enter__(self):
        """Start tracing when entering the context."""
        # Create tracer with appropriate filtering
        if self.capture_all:
            self.tracer = FunctionTracer(filter_modules=[])  # Trace everything
        else:
            self.tracer = FunctionTracer(filter_modules=self.filter_modules)
        
        self.tracer.start_tracing()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop tracing when exiting the context."""
        if self.tracer:
            self.tracer.stop_tracing()
        return False
    
    def get_trace(self) -> List[CallEvent]:
        """Get the collected trace events."""
        if self.tracer:
            return self.tracer.get_trace()
        return []
    
    def get_formatted_trace(self, show_returns: bool = True) -> str:
        """Get the trace formatted as a readable string."""
        if self.tracer:
            return self.tracer.format_trace(show_returns=show_returns)
        return "No trace available"
    
    def execute_and_trace(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function within this tracing context and return the result.
        
        Args:
            func: Function to execute
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function
            
        Returns:
            The result of the function call
        """
        if not self.tracer or not self.tracer.is_tracing:
            raise RuntimeError("TracingContext must be used as a context manager")
        
        result = func(*args, **kwargs)
        self.result = result
        return result


def trace_calls(
    filter_modules: Optional[List[str]] = None,
    capture_all: bool = False,
    name: Optional[str] = None
) -> TracingContext:
    """
    Create a tracing context manager.
    
    Args:
        filter_modules: List of module patterns to trace
        capture_all: If True, captures all function calls
        name: Optional name for this tracing session
        
    Returns:
        TracingContext instance
        
    Example:
        with trace_calls() as tracer:
            result = my_function("arg1", "arg2")
        
        print(tracer.get_formatted_trace())
    """
    return TracingContext(
        filter_modules=filter_modules,
        capture_all=capture_all,
        name=name
    )


@contextmanager
def trace_execution(func: Callable, *args, **kwargs):
    """
    Context manager that traces a specific function execution.
    
    Args:
        func: Function to execute and trace
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
        
    Yields:
        Dictionary with 'result' and 'trace' keys
        
    Example:
        with trace_execution(my_function, "arg1", "arg2") as execution:
            pass
            
        print(f"Result: {execution['result']}")
        print(f"Trace: {execution['trace']}")
    """
    tracer = FunctionTracer()
    execution_data = {'result': None, 'trace': None}
    
    try:
        tracer.start_tracing()
        result = func(*args, **kwargs)
        execution_data['result'] = result
        execution_data['trace'] = tracer.format_trace()
        yield execution_data
    finally:
        tracer.stop_tracing()


class TraceSession:
    """
    A session manager for collecting multiple traces with context.
    Useful for complex testing scenarios or debugging sessions.
    """
    
    def __init__(self, name: str = "TraceSession"):
        """
        Initialize a trace session.
        
        Args:
            name: Name for this session
        """
        self.name = name
        self.traces = []
        self.current_context = None
    
    def start_context(
        self, 
        context_name: str,
        filter_modules: Optional[List[str]] = None
    ) -> TracingContext:
        """
        Start a new tracing context within this session.
        
        Args:
            context_name: Name for this context
            filter_modules: Module patterns to trace
            
        Returns:
            TracingContext instance
        """
        context = TracingContext(
            filter_modules=filter_modules,
            name=context_name
        )
        self.current_context = context
        return context
    
    def save_current_trace(self, label: Optional[str] = None):
        """
        Save the current context's trace to the session.
        
        Args:
            label: Optional label for this trace
        """
        if self.current_context and self.current_context.tracer:
            trace_data = {
                'label': label or f"trace_{len(self.traces)}",
                'context_name': self.current_context.name,
                'events': self.current_context.get_trace(),
                'formatted': self.current_context.get_formatted_trace()
            }
            self.traces.append(trace_data)
    
    def get_session_summary(self) -> str:
        """Get a summary of all traces in this session."""
        if not self.traces:
            return f"Session '{self.name}': No traces collected"
        
        lines = [f"=== Trace Session: {self.name} ==="]
        lines.append(f"Total traces: {len(self.traces)}")
        lines.append("")
        
        for i, trace in enumerate(self.traces):
            lines.append(f"--- Trace {i + 1}: {trace['label']} ---")
            lines.append(f"Context: {trace['context_name']}")
            lines.append(trace['formatted'])
            lines.append("")
        
        return "\n".join(lines)
    
    def clear(self):
        """Clear all traces from this session."""
        self.traces.clear()
        self.current_context = None


# Convenience functions for common patterns

def trace_function_call(func: Callable, *args, **kwargs) -> tuple:
    """
    Quickly trace a single function call.
    
    Args:
        func: Function to trace
        *args: Arguments to pass
        **kwargs: Keyword arguments to pass
        
    Returns:
        Tuple of (result, formatted_trace)
    """
    with trace_calls() as tracer:
        result = tracer.execute_and_trace(func, *args, **kwargs)
    
    return result, tracer.get_formatted_trace()


def compare_traces(*funcs_and_args) -> str:
    """
    Compare traces from multiple function calls.
    
    Args:
        *funcs_and_args: Tuples of (func, args, kwargs) to trace and compare
        
    Returns:
        Formatted comparison string
        
    Example:
        comparison = compare_traces(
            (func1, ("arg1",), {}),
            (func2, ("arg2",), {})
        )
    """
    results = []
    
    for i, func_spec in enumerate(funcs_and_args):
        if len(func_spec) == 2:
            func, args = func_spec
            kwargs = {}
        elif len(func_spec) == 3:
            func, args, kwargs = func_spec
        else:
            raise ValueError("Each function spec must be (func, args) or (func, args, kwargs)")
        
        result, trace = trace_function_call(func, *args, **kwargs)
        results.append({
            'index': i + 1,
            'function': func.__name__,
            'result': result,
            'trace': trace
        })
    
    # Format comparison
    lines = ["=== Function Call Comparison ==="]
    for result in results:
        lines.append(f"\n--- Call {result['index']}: {result['function']} ---")
        lines.append(f"Result: {result['result']}")
        lines.append("Trace:")
        lines.append(result['trace'])
    
    return "\n".join(lines)