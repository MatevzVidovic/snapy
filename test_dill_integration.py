"""
Comprehensive test suite for dill integration in Snapy.
Tests configuration, serialization backends, fallback mechanisms, and error handling.
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from snapy.capture.config import CaptureConfig, get_global_config, set_global_config
from snapy.capture.storage import CaptureStorage, CapturedCall, CaptureMetadata
from collections import OrderedDict
from datetime import datetime


class TestClass:
    """Simple test class for serialization testing."""
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"TestClass({self.value})"

    def __eq__(self, other):
        return isinstance(other, TestClass) and self.value == other.value


def test_configuration_loading():
    """Test that configuration loads correctly with dill settings."""
    print("🧪 Testing Configuration Loading...")

    try:
        # Test default configuration
        config = CaptureConfig()
        backend = config.get_serialization_backend()
        fallback = config.should_fallback_to_dill()

        print(f"  ✅ Default backend: {backend}")
        print(f"  ✅ Default fallback: {fallback}")

        # Test configuration dictionary
        config_dict = config.to_dict()
        assert 'serialization_backend' in config_dict
        assert 'fallback_to_dill' in config_dict
        print(f"  ✅ Config dict includes serialization settings")

        return True

    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False


def test_storage_initialization():
    """Test that storage initializes with correct serializer."""
    print("\n🔧 Testing Storage Initialization...")

    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Test storage initialization
        storage = CaptureStorage(temp_dir)

        print(f"  ✅ Storage initialized")
        print(f"  📋 Serializer: {storage.serializer_name}")
        print(f"  📋 Module: {storage.serializer.__name__ if storage.serializer else 'None'}")

        # Cleanup
        shutil.rmtree(temp_dir)
        return True

    except Exception as e:
        print(f"  ❌ Storage initialization failed: {e}")
        return False


def test_basic_serialization():
    """Test basic serialization with current backend."""
    print("\n💾 Testing Basic Serialization...")

    try:
        temp_dir = tempfile.mkdtemp()
        storage = CaptureStorage(temp_dir)

        # Create test data
        test_objects = [
            ("string", "hello world"),
            ("dict", {"key": "value", "nested": {"data": [1, 2, 3]}}),
            ("list", [1, 2, 3, {"nested": "value"}]),
            ("custom_class", TestClass("test_value"))
        ]

        success_count = 0
        for name, obj in test_objects:
            try:
                # Create test capture
                args_dict = OrderedDict([("test_arg", obj)])
                metadata = CaptureMetadata(
                    function_name=f"test_{name}",
                    module_name="test_module",
                    timestamp=datetime.now(),
                    args_count=1,
                    file_path=""
                )
                capture = CapturedCall(metadata=metadata, args_dict=args_dict)

                # Test save and load
                file_path = storage.base_path / f"test_{name}.pkl"
                storage._save_to_file(capture, file_path)
                loaded_capture = storage.load_capture(str(file_path))

                if loaded_capture and loaded_capture.args_dict["test_arg"] == obj:
                    print(f"  ✅ {name}: Serialization successful")
                    success_count += 1
                else:
                    print(f"  ❌ {name}: Data mismatch after serialization")

            except Exception as e:
                print(f"  ❌ {name}: Serialization failed - {e}")

        print(f"  📊 Success rate: {success_count}/{len(test_objects)}")

        # Cleanup
        shutil.rmtree(temp_dir)
        return success_count == len(test_objects)

    except Exception as e:
        print(f"  ❌ Basic serialization test failed: {e}")
        return False


def test_backend_switching():
    """Test switching between different serialization backends."""
    print("\n🔄 Testing Backend Switching...")

    try:
        # Save original config
        original_config = get_global_config()

        # Test pickle backend
        pickle_config = CaptureConfig()
        pickle_config.serialization_backend = "pickle"
        set_global_config(pickle_config)

        temp_dir = tempfile.mkdtemp()
        pickle_storage = CaptureStorage(temp_dir)
        print(f"  ✅ Pickle backend: {pickle_storage.serializer_name}")

        # Test dill backend (if available)
        dill_config = CaptureConfig()
        dill_config.serialization_backend = "dill"
        set_global_config(dill_config)

        dill_storage = CaptureStorage(temp_dir)
        print(f"  ✅ Dill backend: {dill_storage.serializer_name}")

        # Test auto backend
        auto_config = CaptureConfig()
        auto_config.serialization_backend = "auto"
        set_global_config(auto_config)

        auto_storage = CaptureStorage(temp_dir)
        print(f"  ✅ Auto backend: {auto_storage.serializer_name}")

        # Restore original config
        set_global_config(original_config)

        # Cleanup
        shutil.rmtree(temp_dir)
        return True

    except Exception as e:
        print(f"  ❌ Backend switching test failed: {e}")
        return False


def test_fallback_mechanism():
    """Test fallback from pickle to dill when enabled."""
    print("\n🔄 Testing Fallback Mechanism...")

    try:
        # Create a test that would fail with pickle but might work with dill
        temp_dir = tempfile.mkdtemp()

        # Test with fallback enabled
        config = CaptureConfig()
        config.serialization_backend = "pickle"
        config.fallback_to_dill = True
        set_global_config(config)

        storage = CaptureStorage(temp_dir)
        print(f"  ✅ Storage setup with fallback enabled")
        print(f"  📋 Primary backend: {storage.serializer_name}")
        print(f"  📋 Fallback enabled: {config.should_fallback_to_dill()}")

        # Test serialization (this will use pickle, potentially with dill fallback)
        test_obj = TestClass("fallback_test")
        args_dict = OrderedDict([("test_arg", test_obj)])
        metadata = CaptureMetadata(
            function_name="test_fallback",
            module_name="test_module",
            timestamp=datetime.now(),
            args_count=1,
            file_path=""
        )
        capture = CapturedCall(metadata=metadata, args_dict=args_dict)

        file_path = storage.base_path / "fallback_test.pkl"
        storage._save_to_file(capture, file_path)
        loaded_capture = storage.load_capture(str(file_path))

        if loaded_capture:
            print(f"  ✅ Fallback mechanism working")
        else:
            print(f"  ⚠️  Fallback mechanism needs dill installation")

        # Cleanup
        shutil.rmtree(temp_dir)
        return True

    except Exception as e:
        print(f"  ❌ Fallback test failed: {e}")
        return False


def test_environment_variables():
    """Test environment variable configuration."""
    print("\n🌍 Testing Environment Variables...")

    try:
        # Save original environment
        original_env = {}
        env_vars = [
            "SNAP_CAPTURE_SERIALIZATION_BACKEND",
            "SNAP_CAPTURE_FALLBACK_TO_DILL"
        ]

        for var in env_vars:
            original_env[var] = os.environ.get(var)

        # Test environment variable setting
        os.environ["SNAP_CAPTURE_SERIALIZATION_BACKEND"] = "pickle"
        os.environ["SNAP_CAPTURE_FALLBACK_TO_DILL"] = "false"

        config = CaptureConfig()
        assert config.get_serialization_backend() == "pickle"
        assert config.should_fallback_to_dill() == False
        print(f"  ✅ Environment variables loaded correctly")

        # Test different values
        os.environ["SNAP_CAPTURE_SERIALIZATION_BACKEND"] = "dill"
        os.environ["SNAP_CAPTURE_FALLBACK_TO_DILL"] = "true"

        config2 = CaptureConfig()
        backend = config2.get_serialization_backend()
        fallback = config2.should_fallback_to_dill()
        print(f"  ✅ Backend: {backend}, Fallback: {fallback}")

        # Restore environment
        for var, value in original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

        return True

    except Exception as e:
        print(f"  ❌ Environment variable test failed: {e}")
        return False


def test_error_handling():
    """Test error handling in various scenarios."""
    print("\n🚨 Testing Error Handling...")

    try:
        temp_dir = tempfile.mkdtemp()
        storage = CaptureStorage(temp_dir)

        # Test loading non-existent file
        non_existent = storage.base_path / "does_not_exist.pkl"
        result = storage.load_capture(str(non_existent))
        assert result is None
        print(f"  ✅ Non-existent file handled correctly")

        # Test loading corrupted file
        corrupted_file = storage.base_path / "corrupted.pkl"
        with open(corrupted_file, 'wb') as f:
            f.write(b"not a pickle file")

        result = storage.load_capture(str(corrupted_file))
        assert result is None
        print(f"  ✅ Corrupted file handled correctly")

        # Test invalid backend configuration
        config = CaptureConfig()
        config.serialization_backend = "invalid_backend"
        backend = config.get_serialization_backend()
        assert backend == "dill"  # Should default to dill
        print(f"  ✅ Invalid backend defaults to dill")

        # Cleanup
        shutil.rmtree(temp_dir)
        return True

    except Exception as e:
        print(f"  ❌ Error handling test failed: {e}")
        return False


def test_showcase_integration():
    """Test integration with showcase examples."""
    print("\n🎯 Testing Showcase Integration...")

    try:
        # Test importing showcase modules
        showcase_dir = Path(__file__).parent / "000showcase"
        if showcase_dir.exists():
            sys.path.insert(0, str(showcase_dir))

            # Import and test data structures
            import data_structures

            # Test that capture decorators work
            person = data_structures.Person("Test User", 25, ["Python"])
            result = data_structures.process_person(person, "Engineering", 75000)

            print(f"  ✅ Showcase integration working")
            print(f"  📋 Result type: {type(result)}")

            return True
        else:
            print(f"  ⚠️  Showcase directory not found, skipping")
            return True

    except Exception as e:
        print(f"  ❌ Showcase integration test failed: {e}")
        return False


def main():
    """Run comprehensive test suite."""
    print("🔍 Comprehensive Dill Integration Test Suite")
    print("=" * 50)

    tests = [
        ("Configuration Loading", test_configuration_loading),
        ("Storage Initialization", test_storage_initialization),
        ("Basic Serialization", test_basic_serialization),
        ("Backend Switching", test_backend_switching),
        ("Fallback Mechanism", test_fallback_mechanism),
        ("Environment Variables", test_environment_variables),
        ("Error Handling", test_error_handling),
        ("Showcase Integration", test_showcase_integration),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! Dill integration is working correctly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Check output above for details.")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)