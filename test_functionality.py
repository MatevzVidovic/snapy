#!/usr/bin/env python3
"""
Simple functionality test for the restructured Snapy framework.
Tests basic imports and functionality without requiring pytest.
"""

import sys
import os
sys.path.insert(0, 'src')

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")

    # Test unified imports
    try:
        from snapy import capture_args, FunctionTracer, TracedSnapshot
        print("✓ Unified imports working")
    except ImportError as e:
        print(f"✗ Unified imports failed: {e}")
        return False

    # Test module-specific imports
    try:
        from snapy.capture import capture_args, load_capture
        from snapy.testing import FunctionTracer, CallEvent
        print("✓ Module-specific imports working")
    except ImportError as e:
        print(f"✗ Module imports failed: {e}")
        return False

    return True

def test_capture_functionality():
    """Test basic capture functionality."""
    print("\nTesting capture functionality...")

    from snapy.capture import capture_args, load_capture, has_capture

    @capture_args(path="./test_captures")
    def test_function(x, y, operation="add"):
        if operation == "add":
            return x + y
        elif operation == "multiply":
            return x * y
        return 0

    # Execute function to create capture
    result1 = test_function(3, 4)
    print(f"✓ Function executed: {result1}")

    # Check if capture exists (must specify same path!)
    if has_capture("test_function", path="./test_captures"):
        print("✓ Capture created successfully")

        # Load and replay
        args, kwargs = load_capture("test_function", path="./test_captures")
        result2 = test_function(*args, **kwargs)
        print(f"✓ Capture loaded and replayed: {result2}")

        if result1 == result2:
            print("✓ Results match!")
            return True
        else:
            print(f"✗ Results don't match: {result1} vs {result2}")
            return False
    else:
        print("✗ Capture not found")
        return False

def test_tracing_functionality():
    """Test basic tracing functionality."""
    print("\nTesting tracing functionality...")

    from snapy.testing import FunctionTracer

    def traced_function(a, b):
        def helper(x):
            return x * 2

        result1 = helper(a)
        result2 = helper(b)
        return result1 + result2

    tracer = FunctionTracer()

    with tracer:
        result = traced_function(3, 4)

    events = tracer.get_trace()
    print(f"✓ Function executed with tracing: {result}")
    print(f"✓ Captured {len(events)} events")

    # Check that we captured some events
    if len(events) > 0:
        print("✓ Events captured successfully")
        return True
    else:
        print("✗ No events captured")
        return False

def test_integration():
    """Test capture + tracing integration."""
    print("\nTesting integration...")

    from snapy.capture import capture_args, load_capture
    from snapy.testing import FunctionTracer

    @capture_args(path="./integration_test")
    def integration_function(data, multiplier=2):
        return data * multiplier

    # Execute to create capture
    result1 = integration_function("test", 3)
    print(f"✓ Integration function executed: {result1}")

    # Load capture and execute with tracing
    args, kwargs = load_capture("integration_function", path="./integration_test")
    tracer = FunctionTracer()

    with tracer:
        result2 = integration_function(*args, **kwargs)

    events = tracer.get_trace()
    print(f"✓ Replayed with tracing: {result2}")
    print(f"✓ Captured {len(events)} trace events")

    return result1 == result2

def main():
    """Run all tests."""
    print("=" * 60)
    print("SNAPY FRAMEWORK FUNCTIONALITY TEST")
    print("=" * 60)

    tests = [
        ("Import Tests", test_imports),
        ("Capture Functionality", test_capture_functionality),
        ("Tracing Functionality", test_tracing_functionality),
        ("Integration Test", test_integration),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                print(f"✓ {test_name}: PASSED")
                passed += 1
            else:
                print(f"✗ {test_name}: FAILED")
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {e}")

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED! Framework is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Framework needs debugging.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)