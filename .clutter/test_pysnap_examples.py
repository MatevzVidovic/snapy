"""
Unit tests for PySnap functionality - Educational examples
These tests demonstrate how PySnap works and what you can tweak to experiment.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from types import FrameType

# Import the modules we're testing
sys.path.append('src')
from pysnap.tracer import FunctionTracer, CallEvent
from pysnap.context import trace_calls
from pysnap.snapshot import TracedSnapshot


class TestCallEvent:
    """Test the CallEvent dataclass - the building block of traces."""

    def test_call_event_creation(self):
        """Test basic CallEvent creation."""
        event = CallEvent(
            event_type='call',
            function_name='test_func',
            filename='/test.py',
            line_number=10,
            args={'x': 1, 'y': 2},
            depth=0
        )

        assert event.event_type == 'call'
        assert event.function_name == 'test_func'
        assert event.args == {'x': 1, 'y': 2}
        assert event.return_value is None  # Default value

    def test_return_event_creation(self):
        """Test CallEvent for return events."""
        event = CallEvent(
            event_type='return',
            function_name='test_func',
            filename='/test.py',
            line_number=15,
            return_value='result',
            depth=0
        )

        assert event.event_type == 'return'
        assert event.return_value == 'result'
        assert event.args == {}  # Default empty dict


class TestFunctionTracer:
    """Test the core FunctionTracer class."""

    def test_tracer_initialization(self):
        """Test tracer starts in correct state."""
        tracer = FunctionTracer()

        assert tracer.events == []
        assert tracer.call_stack == []
        assert tracer.is_tracing is False
        assert tracer.filter_modules == []

    def test_tracer_with_module_filter(self):
        """Test tracer with specific modules to trace."""
        tracer = FunctionTracer(filter_modules=['myproject', 'src'])

        assert tracer.filter_modules == ['myproject', 'src']

    def test_should_trace_frame_filtering(self):
        """Test the frame filtering logic."""
        tracer = FunctionTracer()

        # Mock frame object
        mock_frame = MagicMock()
        mock_frame.f_code.co_filename = '/home/user/myproject/main.py'
        mock_frame.f_code.co_name = 'my_function'

        # Should trace user code
        assert tracer.should_trace_frame(mock_frame) is True

        # Should NOT trace system modules
        mock_frame.f_code.co_filename = '/usr/lib/python3.8/json/__init__.py'
        assert tracer.should_trace_frame(mock_frame) is False

        # Should NOT trace dunder methods
        mock_frame.f_code.co_name = '__init__'
        mock_frame.f_code.co_filename = '/home/user/myproject/main.py'
        assert tracer.should_trace_frame(mock_frame) is False

    def test_extract_args_from_frame(self):
        """Test argument extraction from frame."""
        tracer = FunctionTracer()

        # Mock frame with function arguments
        mock_frame = MagicMock()
        mock_frame.f_code.co_argcount = 2
        mock_frame.f_code.co_varnames = ('x', 'y', 'local_var')
        mock_frame.f_locals = {'x': 10, 'y': 20, 'local_var': 'ignored'}

        args = tracer.extract_args(mock_frame)

        assert args == {'x': 10, 'y': 20}
        assert 'local_var' not in args  # Only function args, not locals


class TestTraceCalls:
    """Test the trace_calls context manager."""

    def test_context_manager_basic_usage(self):
        """Test basic context manager functionality."""
        def sample_function(x, y):
            return x + y

        def another_function(a):
            return sample_function(a, 5)

        with trace_calls(filter_modules=['test_pysnap']) as tracer:
            result = another_function(10)

        assert result == 15
        assert tracer.events  # Should have captured some events

        # Check we captured the right function calls
        function_names = [event.function_name for event in tracer.events]
        assert 'another_function' in function_names
        assert 'sample_function' in function_names

    def test_context_manager_preserves_original_trace(self):
        """Test that original trace function is restored."""
        original_trace = sys.gettrace()

        def dummy_function():
            return "test"

        with trace_calls() as tracer:
            dummy_function()

        # Original trace should be restored
        assert sys.gettrace() == original_trace

    def test_formatted_trace_output(self):
        """Test the formatted trace string output."""
        def outer_function(value):
            return inner_function(value * 2)

        def inner_function(value):
            return value + 1

        with trace_calls(filter_modules=['test_pysnap']) as tracer:
            result = outer_function(5)

        formatted = tracer.get_formatted_trace()

        # Should contain both functions
        assert 'outer_function' in formatted
        assert 'inner_function' in formatted
        # Should show the nested structure
        assert '├─' in formatted or '└─' in formatted


class TestTracedSnapshot:
    """Test the TracedSnapshot class for snapshot testing."""

    def test_traced_snapshot_creation(self):
        """Test basic TracedSnapshot functionality."""
        snapshot = TracedSnapshot()

        assert snapshot.tracer is not None
        assert snapshot.captured_trace is None

    def test_capture_trace_functionality(self):
        """Test capturing a function trace for snapshotting."""
        def test_function(x, y):
            return x * y

        def helper_function(val):
            return test_function(val, 2)

        snapshot = TracedSnapshot()
        result = snapshot.capture_trace(helper_function, 5)

        assert result == 10  # 5 * 2
        assert snapshot.captured_trace is not None
        assert len(snapshot.captured_trace) > 0

        # Should have captured both function calls
        function_names = [event.function_name for event in snapshot.captured_trace]
        assert 'helper_function' in function_names
        assert 'test_function' in function_names

    def test_capture_trace_with_multiple_args(self):
        """Test capturing function with multiple arguments."""
        def complex_function(a, b, c=None):
            if c:
                return a + b + c
            return a + b

        snapshot = TracedSnapshot()
        result = snapshot.capture_trace(complex_function, 1, 2, c=3)

        assert result == 6

        # Find the call event and check arguments were captured
        call_events = [e for e in snapshot.captured_trace if e.event_type == 'call']
        assert len(call_events) > 0

        complex_call = next(e for e in call_events if e.function_name == 'complex_function')
        assert complex_call.args['a'] == 1
        assert complex_call.args['b'] == 2
        assert complex_call.args['c'] == 3


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""

    def test_recursive_function_tracing(self):
        """Test tracing recursive functions."""
        def factorial(n):
            if n <= 1:
                return 1
            return n * factorial(n - 1)

        with trace_calls(filter_modules=['test_pysnap']) as tracer:
            result = factorial(4)

        assert result == 24

        # Should capture multiple calls to factorial
        factorial_calls = [e for e in tracer.events
                          if e.function_name == 'factorial' and e.event_type == 'call']
        assert len(factorial_calls) == 4  # factorial(4), factorial(3), factorial(2), factorial(1)

        # Check depth increases with recursion
        depths = [call.depth for call in factorial_calls]
        assert max(depths) >= 3  # Should have nested calls

    def test_exception_handling_in_trace(self):
        """Test how tracer handles exceptions."""
        def function_that_raises():
            raise ValueError("Test exception")

        def function_that_catches():
            try:
                function_that_raises()
            except ValueError:
                return "caught"

        with trace_calls(filter_modules=['test_pysnap']) as tracer:
            result = function_that_catches()

        assert result == "caught"

        # Should still capture function calls even with exceptions
        function_names = [event.function_name for event in tracer.events]
        assert 'function_that_catches' in function_names
        assert 'function_that_raises' in function_names


# Example functions to experiment with
def mathematical_operations(x, y):
    """Example function for experimentation."""
    def add(a, b):
        return a + b

    def multiply(a, b):
        return a * b

    sum_result = add(x, y)
    product_result = multiply(x, y)

    return {
        'sum': sum_result,
        'product': product_result,
        'average': sum_result / 2
    }


def data_processing_pipeline(data):
    """Example data processing function."""
    def validate_data(data):
        if not isinstance(data, list):
            raise TypeError("Data must be a list")
        return True

    def filter_positive(data):
        return [x for x in data if x > 0]

    def calculate_stats(data):
        return {
            'count': len(data),
            'sum': sum(data),
            'average': sum(data) / len(data) if data else 0
        }

    validate_data(data)
    filtered = filter_positive(data)
    stats = calculate_stats(filtered)

    return stats


class TestExperimentationExamples:
    """Tests that show what you can tweak to experiment."""

    def test_mathematical_operations_trace(self):
        """Experiment: Change the input values and see how trace changes."""
        # Try changing these values and run the test to see different traces
        x_value = 10  # Try: 5, 100, -3
        y_value = 3   # Try: 7, 0, -1

        with trace_calls(filter_modules=['test_pysnap']) as tracer:
            result = mathematical_operations(x_value, y_value)

        # Print the trace to see the function call tree
        print("\n" + "="*50)
        print(f"Mathematical Operations Trace (x={x_value}, y={y_value}):")
        print("="*50)
        print(tracer.get_formatted_trace())

        assert result['sum'] == x_value + y_value
        assert result['product'] == x_value * y_value

    def test_data_processing_pipeline_trace(self):
        """Experiment: Change the input data and see how processing changes."""
        # Try different data sets:
        test_data = [1, 2, 3, 4, 5]  # Try: [-1, 0, 1], [10, -5, 3], []

        snapshot = TracedSnapshot()
        result = snapshot.capture_trace(data_processing_pipeline, test_data)

        print("\n" + "="*50)
        print(f"Data Processing Trace (data={test_data}):")
        print("="*50)

        # Print detailed trace information
        for event in snapshot.captured_trace:
            if event.event_type == 'call':
                print(f"{'  ' * event.depth}📞 {event.function_name}({event.args})")
            else:
                print(f"{'  ' * event.depth}📤 {event.function_name} → {event.return_value}")

        assert 'count' in result
        assert 'sum' in result
        assert 'average' in result


if __name__ == "__main__":
    # Run some example traces when script is executed directly
    print("PySnap Example Traces")
    print("="*40)

    # Example 1: Simple function tracing
    with trace_calls(filter_modules=['test_pysnap']) as tracer:
        result = mathematical_operations(7, 3)

    print("\nExample 1 - Mathematical Operations:")
    print(tracer.get_formatted_trace())
    print(f"Result: {result}")

    # Example 2: Data processing
    snapshot = TracedSnapshot()
    result = snapshot.capture_trace(data_processing_pipeline, [1, -2, 3, 4])

    print("\nExample 2 - Data Processing Pipeline:")
    for event in snapshot.captured_trace:
        indent = "  " * event.depth
        if event.event_type == 'call':
            print(f"{indent}→ {event.function_name}({event.args})")
        else:
            print(f"{indent}← {event.function_name} returns {event.return_value}")

    print(f"\nFinal Result: {result}")