"""
Integration tests for the complete PySnap system.
Tests all components working together.
"""

from snapy import FunctionTracer, TracedSnapshot


def helper_function(x):
    """Helper function for testing."""
    return x * 2


def main_function(a, b):
    """Main function that calls helper."""
    return helper_function(a) + helper_function(b)


def complex_workflow(data):
    """Complex workflow with multiple steps."""
    step1 = preprocess(data)
    step2 = process(step1)
    step3 = postprocess(step2)
    return step3


def preprocess(data):
    """Preprocessing step."""
    return data.upper() if isinstance(data, str) else str(data)


def process(data):
    """Processing step."""
    return f"PROCESSED_{data}"


def postprocess(data):
    """Postprocessing step."""
    return f"[{data}]"


class TestIntegration:
    """Integration tests for PySnap components."""
    
    def test_traced_snapshot_integration(self):
        """Test TracedSnapshot with real functions."""
        from snapy.snapshot import create_traced_snapshot
        snapshot = create_traced_snapshot(filter_modules=["test_integration"])
        
        result = snapshot.capture_trace(main_function, 3, 4)
        
        assert result == 14  # helper(3) + helper(4) = 6 + 8 = 14
        
        trace = snapshot.format_trace_snapshot()
        
        # Verify the trace contains all expected elements
        assert 'main_function' in trace
        assert 'helper_function' in trace
        assert 'a=3' in trace
        assert 'b=4' in trace
        assert 'Returns:' in trace
    
    def test_context_manager_integration(self):
        """Test trace_calls context manager."""
        with trace_calls(filter_modules=["test_integration"]) as tracer:
            result1 = main_function(2, 3)
            result2 = helper_function(5)
        
        assert result1 == 10
        assert result2 == 10
        
        formatted = tracer.get_formatted_trace()
        events = tracer.get_trace()
        
        # Should have multiple function calls
        call_events = [e for e in events if e.event_type == 'call']
        assert len(call_events) >= 3  # main_function + 2 helper_function calls + 1 more helper
        
        # Verify function names are captured
        function_names = [e.function_name for e in call_events]
        assert 'main_function' in function_names
        assert 'helper_function' in function_names
    
    def test_decorator_integration(self):
        """Test decorator functionality."""
        @trace_snapshot(filter_modules=["test_integration"])
        def decorated_function(x, y):
            return main_function(x, y)
        
        result = decorated_function(1, 2)
        assert result == 6  # helper(1) + helper(2) = 2 + 4 = 6
        
        # Check that trace data is attached to function
        trace = decorated_function.get_last_trace()
        formatted = decorated_function.get_last_formatted()
        
        assert len(trace) > 0
        assert 'decorated_function' in formatted
        assert 'main_function' in formatted
        assert 'helper_function' in formatted
    
    def test_quick_trace_integration(self):
        """Test quick_trace utility."""
        result, trace = quick_trace(complex_workflow, "test")
        
        assert result == "[PROCESSED_TEST]"
        
        # Verify all workflow steps are traced
        assert 'complex_workflow' in trace
        assert 'preprocess' in trace
        assert 'process' in trace
        assert 'postprocess' in trace
        assert 'data=\'test\'' in trace
    
    def test_multiple_snapshot_captures(self):
        """Test capturing multiple traces in sequence."""
        from snapy.snapshot import create_traced_snapshot
        snapshot = create_traced_snapshot(filter_modules=["test_integration"])
        
        # Capture multiple traces
        result1 = snapshot.capture_trace(main_function, 1, 1)
        result2 = snapshot.capture_trace(helper_function, 5)
        result3 = snapshot.capture_trace(complex_workflow, "data")
        
        assert result1 == 4   # helper(1) + helper(1) = 2 + 2 = 4
        assert result2 == 10  # 5 * 2 = 10
        assert result3 == "[PROCESSED_DATA]"
        
        # Get all traces
        all_traces = snapshot.format_all_traces()
        
        # Should contain all three traces
        assert 'Trace 1' in all_traces
        assert 'Trace 2' in all_traces  
        assert 'Trace 3' in all_traces
        assert 'main_function' in all_traces
        assert 'helper_function' in all_traces
        assert 'complex_workflow' in all_traces
    
    def test_trace_collector_integration(self):
        """Test TraceCollector with decorated functions."""
        collector = TraceCollector()
        
        @trace_snapshot(filter_modules=["test_integration"])
        def func1(x):
            return helper_function(x)
        
        @trace_snapshot(filter_modules=["test_integration"])
        def func2(x):
            return x + 1
        
        # Execute functions
        result1 = func1(3)
        result2 = func2(5)
        
        # Collect traces
        collector.collect_from_function(func1)
        collector.collect_from_function(func2)
        
        combined = collector.get_combined_formatted()
        
        assert 'func1' in combined
        assert 'func2' in combined
        assert 'helper_function' in combined
    
    def test_filter_modules_integration(self):
        """Test module filtering works across all components."""
        # Test with no filter (should trace test functions)
        with trace_calls() as tracer1:
            main_function(1, 1)
        
        events1 = tracer1.get_trace()
        test_events1 = [e for e in events1 if 'test_integration' in e.filename]
        
        # Test with filter (should trace test functions)
        with trace_calls(filter_modules=["test_integration"]) as tracer2:
            main_function(1, 1)
        
        events2 = tracer2.get_trace()
        test_events2 = [e for e in events2 if 'test_integration' in e.filename]
        
        # Both should capture our test functions
        assert len(test_events1) > 0
        assert len(test_events2) > 0
    
    def test_error_handling_integration(self):
        """Test behavior when traced functions raise exceptions."""
        def error_function():
            raise ValueError("Test error")
        
        def caller_function():
            try:
                error_function()
            except ValueError:
                return "caught"
        
        # Should still trace even when exceptions occur
        with trace_calls(filter_modules=["test_integration"]) as tracer:
            result = caller_function()
        
        assert result == "caught"
        
        events = tracer.get_trace()
        call_events = [e for e in events if e.event_type == 'call']
        
        # Should have traced both functions
        function_names = [e.function_name for e in call_events]
        assert 'caller_function' in function_names
        assert 'error_function' in function_names
    
    def test_complex_data_types_integration(self):
        """Test tracing with complex data types."""
        def process_dict(data):
            return {k: v * 2 for k, v in data.items()}
        
        def process_list(data):
            return [x + 1 for x in data]
        
        def main_processor(data):
            if isinstance(data, dict):
                return process_dict(data)
            elif isinstance(data, list):
                return process_list(data)
            return data
        
        from snapy.snapshot import create_traced_snapshot
        snapshot = create_traced_snapshot(filter_modules=["test_integration"])
        
        # Test with dictionary
        dict_data = {'a': 1, 'b': 2}
        result1 = snapshot.capture_trace(main_processor, dict_data)
        assert result1 == {'a': 2, 'b': 4}
        
        # Test with list
        snapshot.clear()
        list_data = [1, 2, 3]
        result2 = snapshot.capture_trace(main_processor, list_data)
        assert result2 == [2, 3, 4]
        
        # Verify complex data is handled in trace
        formatted = snapshot.format_trace_snapshot()
        assert 'main_processor' in formatted
        assert 'process_list' in formatted


if __name__ == "__main__":
    # Run integration tests manually
    test_instance = TestIntegration()
    
    print("Running integration tests...")
    
    test_instance.test_traced_snapshot_integration()
    print("✓ TracedSnapshot integration")
    
    test_instance.test_context_manager_integration()
    print("✓ Context manager integration")
    
    test_instance.test_decorator_integration()
    print("✓ Decorator integration")
    
    test_instance.test_quick_trace_integration()
    print("✓ Quick trace integration")
    
    test_instance.test_multiple_snapshot_captures()
    print("✓ Multiple snapshot captures")
    
    test_instance.test_filter_modules_integration()
    print("✓ Module filtering integration")
    
    test_instance.test_error_handling_integration()
    print("✓ Error handling integration")
    
    test_instance.test_complex_data_types_integration()
    print("✓ Complex data types integration")
    
    print("\n✓ All integration tests passed!")