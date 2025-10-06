"""
Integration example showing how to use snapy_capture with the existing snapy_testing framework.

This demonstrates combining argument capture with function tracing for comprehensive testing.
"""

from snapy.capture import capture_args, load_capture
from snapy.testing import TracedSnapshot
from snapy.testing.snapshot import create_traced_snapshot


@capture_args()
def complex_business_function(user_id: str, data: dict, options: dict = None):
    """
    A complex business function that we want to both capture arguments for
    and trace execution of for comprehensive testing.
    """
    options = options or {}

    # Simulate complex business logic with nested function calls
    validated_data = validate_user_data(user_id, data)
    processed_data = process_data(validated_data, options)
    result = generate_report(processed_data, options.get('format', 'json'))

    return result


@capture_args()
def validate_user_data(user_id: str, data: dict):
    """Validate user data with argument capture."""
    if not user_id:
        raise ValueError("User ID is required")

    if not isinstance(data, dict) or not data:
        raise ValueError("Data must be a non-empty dictionary")

    # Call helper function
    sanitized = sanitize_data(data)

    return {
        "user_id": user_id,
        "data": sanitized,
        "validated_at": "2023-01-01T00:00:00Z"
    }


def sanitize_data(data: dict):
    """Helper function for data sanitization."""
    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially harmful characters
            sanitized[key] = value.replace('<', '').replace('>', '')
        else:
            sanitized[key] = value
    return sanitized


def process_data(validated_data: dict, options: dict):
    """Process validated data."""
    processing_mode = options.get('mode', 'standard')

    if processing_mode == 'fast':
        return fast_process(validated_data)
    elif processing_mode == 'detailed':
        return detailed_process(validated_data)
    else:
        return standard_process(validated_data)


def fast_process(data: dict):
    """Fast processing mode."""
    return {
        "mode": "fast",
        "user_id": data["user_id"],
        "summary": f"Fast processed {len(data['data'])} items"
    }


def detailed_process(data: dict):
    """Detailed processing mode."""
    return {
        "mode": "detailed",
        "user_id": data["user_id"],
        "items": list(data["data"].keys()),
        "details": {key: f"processed_{key}" for key in data["data"].keys()}
    }


def standard_process(data: dict):
    """Standard processing mode."""
    return {
        "mode": "standard",
        "user_id": data["user_id"],
        "processed_items": len(data["data"]),
        "data_hash": hash(str(sorted(data["data"].items())))
    }


def generate_report(processed_data: dict, format_type: str = 'json'):
    """Generate final report."""
    if format_type == 'json':
        return {
            "report": processed_data,
            "format": "json",
            "generated_at": "2023-01-01T00:00:00Z"
        }
    elif format_type == 'summary':
        return {
            "summary": f"Report for {processed_data.get('user_id', 'unknown')}",
            "format": "summary"
        }
    else:
        raise ValueError(f"Unsupported format: {format_type}")


def test_integration_capture_and_trace(snapshot):
    """
    Test that combines argument capture with function tracing.

    This test demonstrates the power of combining both approaches:
    1. Use captured arguments to replay real function calls
    2. Use tracing to verify the complete execution flow
    """
    # Check if we have captured arguments
    captured_args = load_capture("complex_business_function")

    if captured_args:
        # Use captured arguments
        args, kwargs = captured_args
        print(f"Using captured args: {args}, kwargs: {kwargs}")
    else:
        # Fall back to test arguments
        args = ("test_user_123",)
        kwargs = {
            "data": {"name": "Test User", "email": "test@example.com"},
            "options": {"mode": "detailed", "format": "json"}
        }
        print("Using fallback test arguments")

    # Create traced snapshot to capture execution flow
    traced = create_traced_snapshot(filter_modules=["integration_with_snapy_testing"])

    # Execute function with tracing
    result = traced.capture_trace(complex_business_function, *args, **kwargs)

    # Assert both the result and the execution trace
    trace_output = traced.format_all_traces()

    # Create combined snapshot that includes both result and trace
    combined_output = {
        "function_result": result,
        "execution_trace": trace_output,
        "captured_args_used": captured_args is not None
    }

    assert combined_output == snapshot


def test_validate_user_data_with_captures(snapshot):
    """Test validate_user_data using both captures and tracing."""
    # Try to load captured arguments
    captured = load_capture("validate_user_data")

    if captured:
        args, kwargs = captured
    else:
        # Fallback arguments
        args = ("user456",)
        kwargs = {"data": {"field1": "value1", "field2": "value2"}}

    # Use tracing to see the full execution
    traced = create_traced_snapshot(filter_modules=["integration_with_snapy_testing"])
    result = traced.capture_trace(validate_user_data, *args, **kwargs)

    # Combine result and trace for comprehensive testing
    combined = {
        "result": result,
        "trace": traced.format_all_traces()
    }

    assert combined == snapshot


def run_integration_examples():
    """Run examples to generate both captures and demonstrate integration."""
    print("Running integration examples...")

    # Example 1: Standard processing
    print("\n1. Standard processing:")
    result1 = complex_business_function(
        user_id="user123",
        data={"name": "John Doe", "email": "john@example.com", "age": 30},
        options={"mode": "standard", "format": "json"}
    )
    print(f"Result: {result1}")

    # Example 2: Detailed processing
    print("\n2. Detailed processing:")
    result2 = complex_business_function(
        user_id="user456",
        data={"product": "Widget", "quantity": 5, "price": 29.99},
        options={"mode": "detailed", "format": "json"}
    )
    print(f"Result: {result2}")

    # Example 3: Fast processing with summary format
    print("\n3. Fast processing:")
    result3 = complex_business_function(
        user_id="user789",
        data={"category": "electronics", "brand": "TechCorp"},
        options={"mode": "fast", "format": "summary"}
    )
    print(f"Result: {result3}")

    # Example 4: Direct validation (also captured)
    print("\n4. Direct validation:")
    validation_result = validate_user_data(
        "direct_user",
        {"field1": "value<script>", "field2": "clean_value"}
    )
    print(f"Validation result: {validation_result}")

    print("\n✓ Integration examples completed!")
    print("  - Function arguments captured in ./snap_capture/")
    print("  - Ready for combined capture + trace testing")


def demonstrate_combined_workflow():
    """Demonstrate the complete workflow of capture + trace testing."""
    print("\n" + "="*60)
    print("COMBINED CAPTURE + TRACE WORKFLOW DEMONSTRATION")
    print("="*60)

    # Step 1: Generate captures by running business logic
    print("\nStep 1: Generate captures by running business functions...")
    run_integration_examples()

    # Step 2: Show available captures
    print("\nStep 2: Available captures:")
    from snapy.capture import CaptureLoader
    loader = CaptureLoader()

    for func_name in loader.list_functions():
        count = loader.get_capture_count(func_name)
        print(f"  - {func_name}: {count} captures")

    # Step 3: Demonstrate combined testing
    print("\nStep 3: Combined testing with latest captures...")

    # Load latest capture for complex function
    latest_capture = loader.load_latest("complex_business_function")
    if latest_capture:
        args, kwargs = latest_capture
        print(f"  Latest capture args: {args}")
        print(f"  Latest capture kwargs: {kwargs}")

        # Execute with tracing
        traced = create_traced_snapshot(filter_modules=["integration_with_snapy_testing"])
        result = traced.capture_trace(complex_business_function, *args, **kwargs)

        print(f"  Execution result: {result}")
        print("\n  Execution trace:")
        print(traced.format_all_traces())

    print("\n✓ Combined workflow demonstration completed!")
    print("\nThis demonstrates how snapy_capture and snapy_testing work together:")
    print("  1. snapy_capture: Saves real function arguments for test replay")
    print("  2. snapy_testing: Traces complete execution flow")
    print("  3. Combined: Comprehensive testing with real data and execution verification")


if __name__ == "__main__":
    demonstrate_combined_workflow()

    # Run tests if pytest is available
    try:
        import pytest
        print("\nRunning integration tests...")
        pytest.main([__file__, "-v", "-s"])
    except ImportError:
        print("\nNote: Install pytest to run the integration tests")