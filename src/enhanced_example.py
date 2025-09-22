"""
Enhanced example demonstrating the full capabilities of PySnap tracing.
Shows various ways to trace function arguments, return values, and nested calls.
"""

from pysnap import TracedSnapshot


def inner(arg1, arg2):
    """Inner helper function."""
    return arg1 + arg2


def outer(arg3, arg4):
    """Outer function that calls inner."""
    return arg3 + arg4 + inner(arg3, arg4)


def complex_function(data, multiplier=2):
    """A more complex function with multiple operations."""
    processed = process_data(data)
    multiplied = multiply_result(processed, multiplier)
    return finalize_result(multiplied)


def process_data(data):
    """Process input data."""
    if isinstance(data, str):
        return data.upper()
    return str(data)


def multiply_result(data, multiplier):
    """Multiply the result."""
    return data * multiplier


def finalize_result(data):
    """Finalize the result."""
    return f"[{data}]"


def demonstrate_all_approaches():
    """Demonstrate all the different tracing approaches."""
    
    print("=== PySnap Enhanced Function Tracing Demo ===\n")

    # Approach 2: TracedSnapshot for testing
    print("2. TracedSnapshot for Testing:")
    print("   - Perfect for unit tests")
    print("   - Syrupy compatible\n")
    
    snapshot = TracedSnapshot()
    result2 = snapshot.capture_trace(outer, "hello", "world")
    
    print("Snapshot format:")
    print(snapshot.format_trace_snapshot())
    print(f"Result: {result2}\n")
    


if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_all_approaches()
    
    print("\n=== Integration Instructions ===")
    print("To integrate PySnap into your existing project:")
    print("1. Install: pip install -e /path/to/pysnap")
    print("2. Import: from pysnap import trace_calls, TracedSnapshot")
    print("3. Use context managers for zero-modification tracing")
    print("4. Use TracedSnapshot in test files for snapshot testing")
    print("5. Add decorators for permanent function tracing")
    print("\nExample test file:")
    print("""
def test_my_function(snapshot):
    from pysnap import TracedSnapshot
    
    traced = TracedSnapshot()
    result = traced.capture_trace(my_function, "arg1", "arg2")
    
    # This creates a snapshot of the entire call tree
    traced.assert_match(snapshot)
    """)