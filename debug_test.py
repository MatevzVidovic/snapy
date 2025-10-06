"""
Debug test to identify why captures aren't being created.
"""

import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from snapy.capture.config import get_global_config
from snapy.capture.storage import CaptureStorage
from snapy import capture_args


def test_config():
    """Test configuration is working."""
    print("🔧 Testing Configuration")
    config = get_global_config()
    print(f"  Enabled: {config.enabled}")
    print(f"  Backend: {config.get_serialization_backend()}")
    print(f"  Default path: {config.default_path}")


def test_storage():
    """Test storage creation."""
    print("\n📦 Testing Storage")
    try:
        storage = CaptureStorage("./debug_captures")
        print(f"  Storage created: {storage.base_path}")
        print(f"  Serializer: {storage.serializer_name}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


@capture_args(path="./debug_captures")
def simple_function(x: int, y: str) -> dict:
    """Simple test function."""
    print(f"  Function called with x={x}, y={y}")
    return {"x": x, "y": y, "result": f"{y}_{x}"}


def test_simple_capture():
    """Test simple capture."""
    print("\n🎯 Testing Simple Capture")
    try:
        result = simple_function(42, "test")
        print(f"  Function result: {result}")

        # Check if capture directory was created
        import os
        if os.path.exists("./debug_captures"):
            files = os.listdir("./debug_captures")
            print(f"  Capture files: {files}")
            return len(files) > 0
        else:
            print("  No capture directory created")
            return False
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    """Run debug tests."""
    print("🔍 Debug Test Suite")
    print("=" * 20)

    test_config()
    storage_ok = test_storage()
    capture_ok = test_simple_capture()

    print(f"\n📊 Results:")
    print(f"  Storage: {'✅' if storage_ok else '❌'}")
    print(f"  Capture: {'✅' if capture_ok else '❌'}")

    if capture_ok:
        print("🎉 Basic functionality working!")
    else:
        print("⚠️  Issue with capture functionality")


if __name__ == "__main__":
    main()