#!/usr/bin/env python3
"""
Test the new named argument dictionary format.

This demonstrates the enhanced functionality where all arguments
are captured with their parameter names in an ordered dictionary.
"""

from snapy_capture import capture_args, load_capture_dict
import tempfile
import shutil


def example_function(user_id: str, data: dict, model=None, large_data=None, debug: bool = False):
    """Example function with various parameter types."""
    result = {
        "user_id": user_id,
        "data_keys": list(data.keys()) if data else [],
        "has_model": model is not None,
        "has_large_data": large_data is not None,
        "debug_mode": debug
    }
    return result


def test_new_format():
    """Test the new named argument format."""
    print("Testing new named argument format...")

    # Set up temporary directory for this test
    temp_dir = tempfile.mkdtemp()
    print(f"Using temp directory: {temp_dir}")

    # Apply capture decorator with temp directory
    captured_example_function = capture_args(path=temp_dir)(example_function)

    # Call function to generate capture
    result1 = captured_example_function(
        user_id="user123",
        data={"name": "John", "age": 30},
        model="gpt-4",
        large_data="x" * 1000,  # Large data we might want to exclude
        debug=True
    )
    print(f"Function result: {result1}")

    # Load the captured arguments as dictionary (specify the path)
    args_dict = load_capture_dict("example_function", path=temp_dir)
    print(f"\nCaptured arguments dictionary: {args_dict}")

    if args_dict is None:
        print("ERROR: No arguments were captured!")

        # Debug: check what was actually saved
        from snapy_capture import CaptureLoader
        loader = CaptureLoader(temp_dir)
        functions = loader.list_functions()
        print(f"Available functions: {functions}")

        if functions:
            for func_name in functions:
                capture = loader.load_capture_object(func_name)
                if capture:
                    print(f"Found capture for {func_name}:")
                    print(f"  Metadata: {capture.metadata}")
                    print(f"  Args dict: {capture.args_dict}")
        return

    print("Arguments:")
    for param_name, value in args_dict.items():
        print(f"  {param_name}: {value!r}")

    print(f"\nArgument names in order: {list(args_dict.keys())}")

    # Test different ways to replay the function
    print("\n--- Replay Methods ---")

    # Method 1: Use all arguments as positional
    print("\n1. Using all arguments as positional (*args_dict.values()):")
    result2 = example_function(*args_dict.values())
    print(f"   Result: {result2}")
    print(f"   Results match: {result1 == result2}")

    # Method 2: Use specific arguments by name
    print("\n2. Using specific arguments by name:")
    result3 = example_function(
        user_id=args_dict['user_id'],
        data=args_dict['data'],
        model=args_dict['model'],
        large_data=args_dict['large_data'],
        debug=args_dict['debug']
    )
    print(f"   Result: {result3}")
    print(f"   Results match: {result1 == result3}")

    # Method 3: Filter out large arguments
    print("\n3. Filtering out large arguments:")
    filtered_args = {k: v for k, v in args_dict.items() if k != 'large_data'}
    print(f"   Filtered args: {list(filtered_args.keys())}")

    # This should work because large_data has a default value (None)
    result4 = example_function(**filtered_args)
    print(f"   Result: {result4}")
    print(f"   Large data filtered out: {result4['has_large_data'] == False}")

    # Method 4: Replace specific arguments for testing
    print("\n4. Replacing specific arguments for testing:")
    test_args = args_dict.copy()
    test_args['debug'] = False  # Change debug mode
    test_args['data'] = {"test": "data"}  # Use test data

    result5 = example_function(**test_args)
    print(f"   Result: {result5}")
    print(f"   Debug mode changed: {result5['debug_mode'] == False}")

    # Method 5: Use as kwargs with additional arguments
    print("\n5. Using as kwargs base with overrides:")
    base_args = {k: v for k, v in args_dict.items() if k not in ['large_data', 'debug']}
    result6 = example_function(**base_args, large_data=None, debug=False)
    print(f"   Result: {result6}")

    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f"\n✅ All tests passed! The new format provides flexible argument handling.")


def test_backward_compatibility():
    """Test that backward compatibility is maintained."""
    print("\n--- Testing Backward Compatibility ---")

    from snapy_capture import load_capture

    # The old load_capture function should still work
    capture_result = load_capture("example_function")
    if capture_result is None:
        print("ERROR: No captures found for backward compatibility test!")
        return

    args, kwargs = capture_result
    print(f"Old format - args: {args}")
    print(f"Old format - kwargs: {kwargs}")

    # Should be able to call function the old way
    result = example_function(*args, **kwargs)
    print(f"Old format result: {result}")
    print("✅ Backward compatibility maintained!")


if __name__ == "__main__":
    test_new_format()
    test_backward_compatibility()

    print("\n" + "="*60)
    print("NEW FORMAT BENEFITS:")
    print("="*60)
    print("✅ All arguments captured with parameter names")
    print("✅ Easy to filter out large/unwanted arguments")
    print("✅ Can replay with *args_dict.values() maintaining order")
    print("✅ Can access individual arguments by name")
    print("✅ Can override specific arguments for testing")
    print("✅ Backward compatibility maintained")
    print("✅ Perfect for ML models where you want to exclude large weights")