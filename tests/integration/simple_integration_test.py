"""
Simple integration tests for basic Snapy functionality.
Tests only the core features that are currently implemented.
"""

from snapy import FunctionTracer, TracedSnapshot
from snapy.testing.snapshot import create_traced_snapshot


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


class TestSimpleIntegration:
    """Simple integration tests for implemented Snapy components."""

    def test_traced_snapshot_basic(self):
        """Test TracedSnapshot with real functions."""
        snapshot = create_traced_snapshot(filter_modules=["simple_integration_test"])

        result = snapshot.capture_trace(main_function, 3, 4)

        assert result == 14  # helper(3) + helper(4) = 6 + 8 = 14

        trace = snapshot.format_all_traces()

        # Verify the trace contains expected elements
        assert 'main_function' in trace
        assert 'helper_function' in trace
        assert 'a=3' in trace
        assert 'b=4' in trace
        assert 'Returns:' in trace
        print("✓ TracedSnapshot basic test passed")

    def test_function_tracer_basic(self):
        """Test FunctionTracer with real functions."""
        tracer = FunctionTracer(filter_modules=["simple_integration_test"])

        with tracer:
            result = main_function(2, 3)

        assert result == 10  # helper(2) + helper(3) = 4 + 6 = 10

        events = tracer.get_trace()
        formatted = tracer.format_trace()

        # Should have multiple function calls
        call_events = [e for e in events if e.event_type == 'call']
        assert len(call_events) >= 3  # main_function + 2 helper_function calls

        # Verify function names are captured
        function_names = [e.function_name for e in call_events]
        assert 'main_function' in function_names
        assert 'helper_function' in function_names

        # Verify formatted trace contains expected content
        assert 'main_function' in formatted
        assert 'helper_function' in formatted
        print("✓ FunctionTracer basic test passed")

    def test_complex_workflow_tracing(self):
        """Test tracing a complex workflow."""
        tracer = FunctionTracer(filter_modules=["simple_integration_test"])

        with tracer:
            result = complex_workflow("test")

        assert result == "[PROCESSED_TEST]"

        events = tracer.get_trace()
        formatted = tracer.format_trace()

        # Verify all workflow steps are traced
        assert 'complex_workflow' in formatted
        assert 'preprocess' in formatted
        assert 'process' in formatted
        assert 'postprocess' in formatted
        print("✓ Complex workflow tracing test passed")

    def test_multiple_traces(self):
        """Test capturing multiple traces in sequence."""
        snapshot = create_traced_snapshot(filter_modules=["simple_integration_test"])

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
        print("✓ Multiple traces test passed")


if __name__ == "__main__":
    # Run integration tests manually
    test_instance = TestSimpleIntegration()

    print("Running simple integration tests...")

    test_instance.test_traced_snapshot_basic()
    test_instance.test_function_tracer_basic()
    test_instance.test_complex_workflow_tracing()
    test_instance.test_multiple_traces()

    print("\n✓ All simple integration tests passed!")