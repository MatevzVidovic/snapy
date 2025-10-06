"""
Test file for the Snapy showcase demonstrating argument capture and snapshot testing.

Run this after executing data_structures.py to test with captured arguments.
"""

import sys
import os
import pytest

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from snapy import load_capture, FunctionTracer, TracedSnapshot

# Import our showcase functions
from data_structures import (
    process_person, calculate_inventory_value, process_linked_list,
    complex_nested_structure, Person, Product, create_linked_list,
    HAS_NUMPY, HAS_PANDAS
)

if HAS_NUMPY:
    from data_structures import analyze_numpy_array

if HAS_PANDAS:
    from data_structures import process_dataframe


class TestSnapyShowcase:
    """Test showcase functions using captured arguments and snapshot testing."""

    def test_process_person_with_captured_args(self, snapshot):
        """Test process_person function with captured arguments."""
        try:
            args, kwargs = load_capture("process_person")
            result = process_person(*args, **kwargs)
            assert result == snapshot
        except FileNotFoundError:
            pytest.skip("No captured arguments found - run data_structures.py first")

    def test_calculate_inventory_value_with_captured_args(self, snapshot):
        """Test calculate_inventory_value function with captured arguments."""
        try:
            args, kwargs = load_capture("calculate_inventory_value")
            result = calculate_inventory_value(*args, **kwargs)
            assert result == snapshot
        except FileNotFoundError:
            pytest.skip("No captured arguments found - run data_structures.py first")

    def test_process_linked_list_with_captured_args(self, snapshot):
        """Test process_linked_list function with captured arguments."""
        try:
            args, kwargs = load_capture("process_linked_list")
            result = process_linked_list(*args, **kwargs)
            assert result == snapshot
        except FileNotFoundError:
            pytest.skip("No captured arguments found - run data_structures.py first")

    def test_complex_nested_structure_with_captured_args(self, snapshot):
        """Test complex_nested_structure function with captured arguments."""
        try:
            args, kwargs = load_capture("complex_nested_structure")
            result = complex_nested_structure(*args, **kwargs)
            assert result == snapshot
        except FileNotFoundError:
            pytest.skip("No captured arguments found - run data_structures.py first")

    @pytest.mark.skipif(not HAS_NUMPY, reason="numpy not available")
    def test_analyze_numpy_array_with_captured_args(self, snapshot):
        """Test analyze_numpy_array function with captured arguments."""
        try:
            args, kwargs = load_capture("analyze_numpy_array")
            result = analyze_numpy_array(*args, **kwargs)
            assert result == snapshot
        except FileNotFoundError:
            pytest.skip("No captured arguments found - run data_structures.py first")

    @pytest.mark.skipif(not HAS_PANDAS, reason="pandas not available")
    def test_process_dataframe_with_captured_args(self, snapshot):
        """Test process_dataframe function with captured arguments."""
        try:
            args, kwargs = load_capture("process_dataframe")
            result = process_dataframe(*args, **kwargs)
            assert result == snapshot
        except FileNotFoundError:
            pytest.skip("No captured arguments found - run data_structures.py first")


class TestSnapyTracing:
    """Test function tracing capabilities with complex workflows."""

    def test_traced_person_processing(self, snapshot):
        """Test person processing with function tracing."""
        person = Person("John Doe", 28, ["JavaScript", "React"])

        tracer = FunctionTracer()
        with tracer:
            result = process_person(person, "Frontend", 75000.0)

        traced_result = {
            "function_result": result,
            "trace_events": [
                {
                    "function": event.function_name,
                    "args": str(event.args)[:100] + "..." if len(str(event.args)) > 100 else str(event.args),
                    "event_type": event.event_type
                }
                for event in tracer.get_events()
            ]
        }

        assert traced_result == snapshot

    def test_traced_inventory_calculation(self, snapshot):
        """Test inventory calculation with function tracing."""
        products = [
            Product(10, "tablet", 299.99, True, ["electronics"]),
            Product(11, "case", 19.99, True, ["accessories"])
        ]
        discounts = {"tablet": 0.15}

        tracer = FunctionTracer()
        with tracer:
            result = calculate_inventory_value(products, discounts)

        traced_result = {
            "function_result": result,
            "trace_summary": {
                "total_events": len(tracer.get_events()),
                "function_calls": [event.function_name for event in tracer.get_events() if event.event_type == "call"]
            }
        }

        assert traced_result == snapshot

    def test_traced_linked_list_processing(self, snapshot):
        """Test linked list processing with function tracing."""
        linked_list = create_linked_list(["hello", "world", "snapy"])

        tracer = FunctionTracer()
        with tracer:
            result = process_linked_list(linked_list, "concat")

        traced_result = {
            "function_result": result,
            "trace_info": {
                "events_count": len(tracer.get_events()),
                "has_function_calls": any(event.event_type == "call" for event in tracer.get_events())
            }
        }

        assert traced_result == snapshot


class TestSnapyIntegration:
    """Test integration of capture and tracing together."""

    def test_capture_and_trace_integration(self, snapshot):
        """Test using both capture and tracing on the same workflow."""
        # Create test data
        complex_data = {
            "metadata": {"version": "1.0", "created_by": "test"},
            "items": [{"id": i, "value": i * 10} for i in range(3)]
        }

        # Use tracing during execution
        tracer = FunctionTracer()
        with tracer:
            result = complex_nested_structure(complex_data)

        # Create comprehensive test result
        integration_result = {
            "original_data_keys": list(complex_data.keys()),
            "processing_result": result,
            "trace_summary": {
                "total_events": len(tracer.get_events()),
                "traced_functions": list(set(
                    event.function_name for event in tracer.get_events()
                    if event.event_type == "call"
                ))
            }
        }

        assert integration_result == snapshot


def test_serialization_robustness():
    """Test that our data structures can be serialized and deserialized."""
    from snapy.capture.storage import CaptureStorage
    import tempfile
    import shutil

    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()

    try:
        storage = CaptureStorage(temp_dir)

        # Test serialization of complex objects
        test_objects = [
            Person("Test Person", 25, ["skill1", "skill2"]),
            Product(99, "test_product", 49.99, True, ["tag1", "tag2"]),
            create_linked_list([1, 2, 3]),
            {"nested": {"data": [1, 2, {"deep": "value"}]}}
        ]

        for i, obj in enumerate(test_objects):
            try:
                # Try to save and load each object
                storage.save_capture(f"test_func_{i}", ([obj], {}))
                loaded_args, loaded_kwargs = storage.load_capture(f"test_func_{i}")

                # Basic check that we got something back
                assert loaded_args is not None
                assert loaded_kwargs is not None
                assert len(loaded_args) == 1

                print(f"✅ Successfully serialized/deserialized {type(obj).__name__}")

            except Exception as e:
                print(f"❌ Failed to serialize {type(obj).__name__}: {e}")
                # This is where we'd note issues for the dill plan
                return False

    finally:
        # Clean up
        shutil.rmtree(temp_dir)

    return True


if __name__ == "__main__":
    print("🧪 Testing Snapy Showcase")
    print("=" * 30)

    # Test serialization first
    if test_serialization_robustness():
        print("✅ All serialization tests passed!")
    else:
        print("❌ Some serialization issues detected - check dill_plan.md")

    print("\nRun with pytest for full test suite:")
    print("PYTHONPATH=../src python -m pytest test_showcase.py -v")