"""
Enhanced example demonstrating the full capabilities of PySnap tracing.
Shows various ways to trace function arguments, return values, and nested calls.
"""

from pysnap import trace_snapshot, trace_calls, TracedSnapshot, quick_trace


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


# Example 1: Using decorator approach
@trace_snapshot()
def decorated_outer(arg3, arg4):
    """Same as outer but decorated for automatic tracing."""
    return arg3 + arg4 + inner(arg3, arg4)


def demonstrate_all_approaches():
    """Demonstrate all the different tracing approaches."""
    
    print("=== PySnap Enhanced Function Tracing Demo ===\n")
    
    # Approach 1: Context Manager (No code changes needed)
    print("1. Context Manager Approach:")
    print("   - No function modification required")
    print("   - Wrap any code block\n")
    
    with trace_calls(filter_modules=["enhanced_example"]) as tracer:
        result1 = outer("ena", "dva")
    
    print("Traced execution:")
    print(tracer.get_formatted_trace())
    print(f"Result: {result1}\n")
    
    # Approach 2: TracedSnapshot for testing
    print("2. TracedSnapshot for Testing:")
    print("   - Perfect for unit tests")
    print("   - Syrupy compatible\n")
    
    snapshot = TracedSnapshot()
    result2 = snapshot.capture_trace(outer, "hello", "world")
    
    print("Snapshot format:")
    print(snapshot.format_trace_snapshot())
    print(f"Result: {result2}\n")
    
    # Approach 3: Decorator approach
    print("3. Decorator Approach:")
    print("   - Automatic tracing")
    print("   - Function-level control\n")
    
    result3 = decorated_outer("test", "123")
    
    print("Decorated function trace:")
    print(decorated_outer.get_last_formatted())
    print(f"Result: {result3}\n")
    
    # Approach 4: Quick trace utility
    print("4. Quick Trace Utility:")
    print("   - One-liner for ad-hoc tracing\n")
    
    result4, trace4 = quick_trace(complex_function, "data", multiplier=3)
    
    print("Quick trace of complex function:")
    print(trace4)
    print(f"Result: {result4}\n")
    
    # Approach 5: Multiple function comparison
    print("5. Multiple Function Tracing:")
    print("   - Compare different executions\n")
    
    snapshot.clear()
    
    # Trace multiple calls
    snapshot.capture_trace(outer, "a", "b")
    snapshot.capture_trace(outer, "x", "y") 
    snapshot.capture_trace(complex_function, "test")
    
    print("Multiple traces:")
    print(snapshot.format_all_traces())


def demonstrate_nested_complexity():
    """Demonstrate tracing of deeply nested function calls."""
    
    def level1(x):
        return level2(x) + 1
    
    def level2(x):
        return level3(x) * 2
    
    def level3(x):
        return len(str(x))
    
    print("\n=== Nested Function Tracing ===")
    
    with trace_calls(filter_modules=["enhanced_example"]) as tracer:
        result = level1("test_string")
    
    print("Deep nesting trace:")
    print(tracer.get_formatted_trace())
    print(f"Final result: {result}")


if __name__ == "__main__":
    # Run all demonstrations
    demonstrate_all_approaches()
    demonstrate_nested_complexity()
    
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