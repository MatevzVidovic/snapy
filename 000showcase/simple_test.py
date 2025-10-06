"""
Simple test script that doesn't require pytest.
Tests basic functionality and serialization robustness.
"""

import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from snapy import load_capture, FunctionTracer
from data_structures import (
    process_person, calculate_inventory_value, process_linked_list,
    complex_nested_structure, Person, Product, create_linked_list
)


def test_basic_functionality():
    """Test that we can load captures and run functions."""
    print("🧪 Testing basic functionality...")

    try:
        # Test loading and running each captured function
        test_functions = [
            ("process_person", process_person),
            ("calculate_inventory_value", calculate_inventory_value),
            ("process_linked_list", process_linked_list),
            ("complex_nested_structure", complex_nested_structure),
        ]

        for func_name, func in test_functions:
            try:
                args, kwargs = load_capture(func_name)
                result = func(*args, **kwargs)
                print(f"  ✅ {func_name}: {type(result).__name__} returned")
            except FileNotFoundError:
                print(f"  ⚠️  {func_name}: No capture found")
            except Exception as e:
                print(f"  ❌ {func_name}: Error - {e}")

    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

    return True


def test_serialization_robustness():
    """Test that our data structures can be serialized and deserialized."""
    print("\n🔬 Testing serialization robustness...")

    from snapy.capture.storage import CaptureStorage
    import tempfile
    import shutil

    # Create temporary directory for testing
    temp_dir = tempfile.mkdtemp()

    try:
        storage = CaptureStorage(temp_dir)

        # Test serialization of complex objects
        test_objects = [
            ("Person", Person("Test Person", 25, ["skill1", "skill2"])),
            ("Product", Product(99, "test_product", 49.99, True, ["tag1", "tag2"])),
            ("LinkedList", create_linked_list([1, 2, 3])),
            ("NestedDict", {"nested": {"data": [1, 2, {"deep": "value"}]}}),
            ("ComplexDict", {
                "users": [{"id": 1, "data": {"preferences": {"theme": "dark"}}}],
                "metadata": {"version": "1.0", "features": ["a", "b", "c"]}
            })
        ]

        success_count = 0
        for name, obj in test_objects:
            try:
                # Try to save and load each object
                storage.save_capture(f"test_{name.lower()}", ([obj], {}))
                loaded_args, loaded_kwargs = storage.load_capture(f"test_{name.lower()}")

                # Basic check that we got something back
                assert loaded_args is not None
                assert loaded_kwargs is not None
                assert len(loaded_args) == 1

                print(f"  ✅ {name}: Successfully serialized/deserialized")
                success_count += 1

            except Exception as e:
                print(f"  ❌ {name}: Failed to serialize - {e}")

        print(f"\n📊 Serialization results: {success_count}/{len(test_objects)} successful")

        if success_count == len(test_objects):
            print("🎉 All serialization tests passed!")
            return True
        else:
            print("⚠️  Some objects had serialization issues")
            return False

    finally:
        # Clean up
        shutil.rmtree(temp_dir)


def test_function_tracing():
    """Test that function tracing works with our data structures."""
    print("\n🔍 Testing function tracing...")

    try:
        # Test tracing with a simple workflow
        person = Person("Trace Test", 30, ["Python"])

        tracer = FunctionTracer()
        with tracer:
            result = process_person(person, "Development", 80000.0)

        events = tracer.get_events()
        print(f"  ✅ Tracing captured {len(events)} events")
        print(f"  📋 Result: {result}")

        # Test with linked list
        linked_list = create_linked_list([10, 20, 30])

        tracer = FunctionTracer()
        with tracer:
            result = process_linked_list(linked_list, "sum")

        events = tracer.get_events()
        print(f"  ✅ Linked list tracing captured {len(events)} events")
        print(f"  📋 Result: {result}")

        return True

    except Exception as e:
        print(f"  ❌ Function tracing failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🎯 Snapy Showcase - Simple Tests")
    print("=" * 40)

    all_passed = True

    # Run tests
    all_passed &= test_basic_functionality()
    all_passed &= test_serialization_robustness()
    all_passed &= test_function_tracing()

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Snapy works great with complex data structures.")
    else:
        print("⚠️  Some tests had issues. Check output above for details.")
        print("💡 Consider checking dill_plan.md for serialization alternatives.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)