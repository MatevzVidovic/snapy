"""
Comprehensive test suite for the PySnap tracer functionality.
"""

import sys
from typing import List
from snapy.testing.tracer import FunctionTracer, CallEvent


def simple_function(x, y):
    """Simple function for testing."""
    return x + y


def nested_function(a, b):
    """Function that calls another function."""
    return simple_function(a, b) * 2


def recursive_function(n):
    """Recursive function for testing."""
    if n <= 1:
        return 1
    return n * recursive_function(n - 1)


class TestFunctionTracer:
    """Test cases for the FunctionTracer class."""
    
    def test_tracer_initialization(self):
        """Test tracer can be initialized."""
        tracer = FunctionTracer()
        assert tracer.filter_modules == []
        assert tracer.events == []
        assert not tracer.is_tracing
    
    def test_tracer_with_filter(self):
        """Test tracer with module filtering."""
        tracer = FunctionTracer(filter_modules=["test_"])
        assert tracer.filter_modules == ["test_"]
    
    def test_simple_function_tracing(self):
        """Test tracing a simple function call."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        with tracer:
            result = simple_function(3, 4)
        
        assert result == 7
        events = tracer.get_trace()
        
        # Should have call and return events
        call_events = [e for e in events if e.event_type == 'call']
        return_events = [e for e in events if e.event_type == 'return']
        
        assert len(call_events) >= 1
        assert len(return_events) >= 1
        
        # Check the simple_function call
        simple_call = next((e for e in call_events if e.function_name == 'simple_function'), None)
        assert simple_call is not None
        assert simple_call.args == {'x': 3, 'y': 4}
        
        # Check the simple_function return
        simple_return = next((e for e in return_events if e.function_name == 'simple_function'), None)
        assert simple_return is not None
        assert simple_return.return_value == 7
    
    def test_nested_function_tracing(self):
        """Test tracing nested function calls."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        with tracer:
            result = nested_function(2, 3)
        
        assert result == 10  # (2 + 3) * 2
        events = tracer.get_trace()
        
        call_events = [e for e in events if e.event_type == 'call']
        
        # Should have both nested_function and simple_function calls
        function_names = [e.function_name for e in call_events]
        assert 'nested_function' in function_names
        assert 'simple_function' in function_names
        
        # Check depth tracking
        nested_call = next(e for e in call_events if e.function_name == 'nested_function')
        simple_call = next(e for e in call_events if e.function_name == 'simple_function')
        
        assert nested_call.depth == 0
        assert simple_call.depth == 1
    
    def test_recursive_function_tracing(self):
        """Test tracing recursive function calls."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        with tracer:
            result = recursive_function(3)
        
        assert result == 6  # 3 * 2 * 1
        events = tracer.get_trace()
        
        call_events = [e for e in events if e.event_type == 'call' and e.function_name == 'recursive_function']
        
        # Should have 3 recursive calls (n=3, n=2, n=1)
        assert len(call_events) == 3
        
        # Check that depths increase with recursion
        depths = [e.depth for e in call_events]
        assert depths == [0, 1, 2]
    
    def test_context_manager(self):
        """Test tracer as context manager."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        assert not tracer.is_tracing
        
        with tracer:
            assert tracer.is_tracing
            simple_function(1, 2)
        
        assert not tracer.is_tracing
        assert len(tracer.get_trace()) > 0
    
    def test_manual_start_stop(self):
        """Test manual start/stop tracing."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        tracer.start_tracing()
        assert tracer.is_tracing
        
        simple_function(5, 6)
        
        tracer.stop_tracing()
        assert not tracer.is_tracing
        
        events = tracer.get_trace()
        assert len(events) > 0
    
    def test_clear_events(self):
        """Test clearing traced events."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        with tracer:
            simple_function(1, 1)
        
        assert len(tracer.get_trace()) > 0
        
        tracer.clear()
        assert len(tracer.get_trace()) == 0
    
    def test_format_trace(self):
        """Test trace formatting."""
        tracer = FunctionTracer(filter_modules=["test_tracer"])
        
        with tracer:
            nested_function(2, 3)
        
        formatted = tracer.format_trace()
        
        # Should contain function names and arguments
        assert 'nested_function' in formatted
        assert 'simple_function' in formatted
        assert 'a=2' in formatted
        assert 'b=3' in formatted
        assert 'Returns:' in formatted
    
    def test_should_trace_frame(self):
        """Test frame filtering logic."""
        tracer = FunctionTracer()
        
        # Create a mock frame
        class MockFrame:
            def __init__(self, filename, function_name):
                self.f_code = MockCode(filename, function_name)
        
        class MockCode:
            def __init__(self, filename, function_name):
                self.co_filename = filename
                self.co_name = function_name
        
        # Test system module filtering
        sys_frame = MockFrame('/usr/lib/python3.9/collections.py', 'function')
        assert not tracer.should_trace_frame(sys_frame)
        
        # Test site-packages filtering
        pkg_frame = MockFrame('/site-packages/some_package/module.py', 'function')
        assert not tracer.should_trace_frame(pkg_frame)
        
        # Test dunder method filtering
        dunder_frame = MockFrame('/my/module.py', '__init__')
        assert not tracer.should_trace_frame(dunder_frame)
        
        # Test regular function
        regular_frame = MockFrame('/my/module.py', 'my_function')
        assert tracer.should_trace_frame(regular_frame)
    
    def test_extract_args(self):
        """Test argument extraction from frame."""
        tracer = FunctionTracer()
        
        # Create a mock frame with locals
        class MockFrame:
            def __init__(self, arg_names, locals_dict):
                self.f_code = MockCode(arg_names)
                self.f_locals = locals_dict
        
        class MockCode:
            def __init__(self, arg_names):
                self.co_varnames = arg_names
                self.co_argcount = len(arg_names)
        
        frame = MockFrame(['x', 'y', 'z'], {'x': 1, 'y': 2, 'z': 3, 'local_var': 4})
        args = tracer.extract_args(frame)
        
        assert args == {'x': 1, 'y': 2, 'z': 3}
        assert 'local_var' not in args


class TestCallEvent:
    """Test cases for CallEvent dataclass."""
    
    def test_call_event_creation(self):
        """Test creating a CallEvent."""
        event = CallEvent(
            event_type='call',
            function_name='test_func',
            filename='test.py',
            line_number=10,
            args={'x': 1, 'y': 2},
            depth=1
        )
        
        assert event.event_type == 'call'
        assert event.function_name == 'test_func'
        assert event.filename == 'test.py'
        assert event.line_number == 10
        assert event.args == {'x': 1, 'y': 2}
        assert event.depth == 1
        assert event.return_value is None
    
    def test_return_event_creation(self):
        """Test creating a return CallEvent."""
        event = CallEvent(
            event_type='return',
            function_name='test_func',
            filename='test.py',
            line_number=15,
            return_value=42,
            depth=0
        )
        
        assert event.event_type == 'return'
        assert event.return_value == 42


if __name__ == "__main__":
    # Run tests manually
    test_instance = TestFunctionTracer()
    
    print("Running tracer tests...")
    
    test_instance.test_tracer_initialization()
    print("✓ Tracer initialization")
    
    test_instance.test_simple_function_tracing()
    print("✓ Simple function tracing")
    
    test_instance.test_nested_function_tracing()
    print("✓ Nested function tracing")
    
    test_instance.test_recursive_function_tracing()
    print("✓ Recursive function tracing")
    
    test_instance.test_context_manager()
    print("✓ Context manager")
    
    test_instance.test_format_trace()
    print("✓ Trace formatting")
    
    event_test = TestCallEvent()
    event_test.test_call_event_creation()
    event_test.test_return_event_creation()
    print("✓ CallEvent creation")
    
    print("\n✓ All tracer tests passed!")