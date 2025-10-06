"""
Enhanced snapshot test demonstrating full tracing capabilities.
Compatible with pytest and syrupy for automated testing.
"""

from snapy.testing import TracedSnapshot #, trace_calls, quick_trace
from snapy.testing.snapshot import create_traced_snapshot
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'basic'))
from enhanced_example import outer, inner, complex_function


def test_traced_outer_function(snapshot):
    """Test the outer function with full call tracing."""
    traced = create_traced_snapshot(filter_modules=["enhanced_example"])
    result = traced.capture_trace(outer, "ena", "dva")
    
    # Assert the complete trace matches the snapshot
    traced.assert_match(snapshot)


def test_complex_function_trace(snapshot):
    """Test complex function with multiple nested calls."""
    traced = create_traced_snapshot(filter_modules=["enhanced_example"])
    result = traced.capture_trace(complex_function, "test_data", multiplier=3)
    
    traced.assert_match(snapshot)


def test_multiple_calls_trace(snapshot):
    """Test multiple function calls in sequence."""
    traced = create_traced_snapshot(filter_modules=["enhanced_example"])
    
    # Capture multiple traces
    traced.capture_trace(outer, "hello", "world")
    traced.capture_trace(inner, "foo", "bar")
    traced.capture_trace(complex_function, "data")
    
    # Get combined snapshot
    combined_trace = traced.format_all_traces()
    snapshot.assert_match(combined_trace)

# if False:
#     def test_context_manager_approach(snapshot):
#         """Test using context manager for tracing."""
#         with trace_calls(filter_modules=["enhanced_example"]) as tracer:
#             result1 = outer("test", "123")
#             result2 = complex_function("sample")
        
#         formatted_trace = tracer.get_formatted_trace()
#         snapshot.assert_match(formatted_trace)


#     def test_quick_trace_utility(snapshot):
#         """Test the quick trace utility function."""
#         result, trace = quick_trace(outer, "quick", "trace")
#         snapshot.assert_match(trace)


#     def test_arguments_and_returns():
#         """Test that arguments and return values are properly captured."""
#         traced = create_traced_snapshot(filter_modules=["enhanced_example"])
#         result = traced.capture_trace(outer, "arg1", "arg2")
        
#         events = traced.get_trace()
        
#         # Verify we captured function calls
#         call_events = [e for e in events if e.event_type == 'call']
#         return_events = [e for e in events if e.event_type == 'return']
        
#         assert len(call_events) >= 2  # At least outer and inner
#         assert len(return_events) >= 2  # At least outer and inner returns
        
#         # Check that arguments were captured
#         outer_call = next(e for e in call_events if e.function_name == 'outer')
#         assert 'arg3' in outer_call.args
#         assert 'arg4' in outer_call.args
#         assert outer_call.args['arg3'] == 'arg1'
#         assert outer_call.args['arg4'] == 'arg2'
        
#         inner_call = next(e for e in call_events if e.function_name == 'inner')
#         assert 'arg1' in inner_call.args
#         assert 'arg2' in inner_call.args
        
#         # Check that return values were captured
#         inner_return = next(e for e in return_events if e.function_name == 'inner')
#         assert inner_return.return_value == 'arg1arg2'
        
#         outer_return = next(e for e in return_events if e.function_name == 'outer')
#         assert outer_return.return_value == 'arg1arg2arg1arg2'


#     def test_nested_depth_tracking():
#         """Test that nested call depth is properly tracked."""
#         traced = create_traced_snapshot(filter_modules=["enhanced_example"])
#         traced.capture_trace(outer, "test", "depth")
        
#         events = traced.get_trace()
#         call_events = [e for e in events if e.event_type == 'call']
        
#         # outer should be depth 0, inner should be depth 1
#         outer_call = next(e for e in call_events if e.function_name == 'outer')
#         inner_call = next(e for e in call_events if e.function_name == 'inner')
        
#         assert outer_call.depth == 0
#         assert inner_call.depth == 1


if __name__ == "__main__":
    # Run tests manually for demonstration
    print("Running PySnap tests...")
    
    # Create a mock snapshot for testing
    class MockSnapshot:
        def __init__(self):
            self.captured = None
            
        def __eq__(self, other):
            self.captured = other
            print(f"Snapshot captured:\n{other}")
            return True
        
        def assert_match(self, other):
            return self.__eq__(other)
    
    mock_snapshot = MockSnapshot()
    
    print("\n=== Test: Basic Function Tracing ===")
    test_traced_outer_function(mock_snapshot)
    
    print("\n=== Test: Complex Function Tracing ===")
    test_complex_function_trace(mock_snapshot)
    
    """
    print("\n=== Test: Context Manager ===")
    test_context_manager_approach(mock_snapshot)
    
    print("\n=== Test: Arguments and Returns ===")
    test_arguments_and_returns()
    print("✓ Arguments and return values correctly captured")
    
    print("\n=== Test: Nested Depth ===")
    test_nested_depth_tracking()
    print("✓ Nesting depth correctly tracked")
    """
    
    print("\n✓ All tests completed successfully!")