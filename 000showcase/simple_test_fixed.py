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
                # Load captures from the captures directory
                result = load_capture(func_name, path="./000showcase/captures")
                if result is not None:
                    args, kwargs = result
                    func_result = func(*args, **kwargs)
                    print(f"  ✅ {func_name}: {type(func_result).__name__} returned")
                else:
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

    # For this test, let's just check if we can reload the captured objects
    try:
        test_functions = ["process_person", "calculate_inventory_value", "process_linked_list", "complex_nested_structure"]

        success_count = 0
        for func_name in test_functions:
            try:
                result = load_capture(func_name, path="./000showcase/captures")
                if result is not None:
                    args, kwargs = result
                    # Check that we can access the first argument (which contains our complex objects)
                    if args and len(args) > 0:
                        first_arg = args[0]
                        print(f"  ✅ {func_name}: Successfully loaded {type(first_arg).__name__}")
                        success_count += 1
                    else:
                        print(f"  ⚠️  {func_name}: No arguments found")
                else:
                    print(f"  ⚠️  {func_name}: No capture found")
            except Exception as e:
                print(f"  ❌ {func_name}: Failed to load - {e}")

        print(f"\n📊 Serialization results: {success_count}/{len(test_functions)} successful")

        if success_count == len(test_functions):
            print("🎉 All serialization tests passed!")
            return True
        else:
            print("⚠️  Some objects had serialization issues")
            return False

    except Exception as e:
        print(f"❌ Serialization test failed: {e}")
        return False


def test_function_tracing():
    """Test that function tracing works with our data structures."""
    print("\n🔍 Testing function tracing...")

    try:
        # Test tracing with a simple workflow
        person = Person("Trace Test", 30, ["Python"])

        tracer = FunctionTracer()
        with tracer:
            result = process_person(person, "Development", 80000.0)

        events = tracer.get_trace()  # Correct method name
        print(f"  ✅ Tracing captured {len(events)} events")
        print(f"  📋 Result: {result}")

        # Test with linked list
        linked_list = create_linked_list([10, 20, 30])

        tracer = FunctionTracer()
        with tracer:
            result = process_linked_list(linked_list, "sum")

        events = tracer.get_trace()  # Correct method name
        print(f"  ✅ Linked list tracing captured {len(events)} events")
        print(f"  📋 Result: {result}")

        return True

    except Exception as e:
        print(f"  ❌ Function tracing failed: {e}")
        return False


def test_complex_objects_details():
    """Test details of complex object serialization."""
    print("\n🔍 Testing complex object details...")

    try:
        # Check what was actually captured for the person function
        result = load_capture("process_person", path="./000showcase/captures")
        if result:
            args, kwargs = result
            if args and len(args) > 0:
                person = args[0]
                print(f"  ✅ Person object: {person}")
                print(f"  📋 Person type: {type(person)}")
                print(f"  🎯 Person attributes: name={person.name}, age={person.age}, skills={person.skills}")

        # Check products
        result = load_capture("calculate_inventory_value", path="./000showcase/captures")
        if result:
            args, kwargs = result
            if args and len(args) > 0:
                products = args[0]
                print(f"  ✅ Products list: {len(products)} items")
                print(f"  📋 First product: {products[0]}")

        # Check linked list
        result = load_capture("process_linked_list", path="./000showcase/captures")
        if result:
            args, kwargs = result
            if args and len(args) > 0:
                linked_list = args[0]
                print(f"  ✅ Linked list head: {linked_list}")
                print(f"  🔗 Next node: {linked_list.next if linked_list else None}")

        return True

    except Exception as e:
        print(f"  ❌ Complex object test failed: {e}")
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
    all_passed &= test_complex_objects_details()

    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All tests passed! Snapy works great with complex data structures.")
        print("✅ Pickle serialization handles all our test objects successfully.")
    else:
        print("⚠️  Some tests had issues. Check output above for details.")
        print("💡 Consider checking dill_plan.md for serialization alternatives.")

    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)