"""
Tests for the capture decorator functionality.
"""

import tempfile
import shutil
import asyncio
from pathlib import Path
import pytest

from snapy_capture.capture import capture_args, CaptureContext, disable_capture, capture_once, capture_minimal
from snapy_capture.config import CaptureConfig, set_global_config
from snapy_capture.storage import CaptureStorage
from snapy_capture.loader import load_capture


class TestCaptureDecorator:
    """Test the @capture_args decorator."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = CaptureConfig()
        self.config.default_path = self.temp_dir
        set_global_config(self.config)

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_basic_capture(self):
        """Test basic function capture."""
        @capture_args()
        def test_function(arg1, arg2, kwarg1=None):
            return f"{arg1}-{arg2}-{kwarg1}"

        # Call the function
        result = test_function("hello", "world", kwarg1="test")

        # Verify function still works
        assert result == "hello-world-test"

        # Verify capture was saved
        captures = load_capture("test_function")
        assert captures is not None
        args, kwargs = captures
        assert args == ("hello", "world")
        assert kwargs == {"kwarg1": "test"}

    def test_capture_with_custom_path(self):
        """Test capture with custom storage path."""
        custom_path = str(Path(self.temp_dir) / "custom")

        @capture_args(path=custom_path)
        def test_function(data):
            return data * 2

        test_function("test")

        # Verify capture in custom path
        storage = CaptureStorage(custom_path)
        captures = storage.list_captures("test_function")
        assert len(captures) == 1

    def test_capture_with_retention(self):
        """Test capture with custom retention policy."""
        @capture_args(retention=1)
        def test_function(value):
            return value

        # Call multiple times
        test_function(1)
        test_function(2)
        test_function(3)

        # Should only keep 1 capture
        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("test_function")
        assert len(captures) == 1
        assert captures[0].args == (3,)

    def test_capture_with_ignore_args(self):
        """Test capture with argument filtering."""
        @capture_args(ignore_args=["sensitive"])
        def test_function(data, sensitive=None):
            return data

        test_function("public_data", sensitive="secret")

        # Load and verify filtering
        args, kwargs = load_capture("test_function")
        assert args == ("public_data",)
        assert kwargs["sensitive"] == "<FILTERED:SENSITIVE>"

    def test_capture_disabled_globally(self):
        """Test capture when globally disabled."""
        # Disable globally
        self.config.enabled = False
        set_global_config(self.config)

        @capture_args()
        def test_function(data):
            return data

        test_function("test")

        # Should not create any captures
        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("test_function")
        assert len(captures) == 0

    def test_capture_disabled_locally(self):
        """Test capture disabled for specific function."""
        @capture_args(enabled=False)
        def test_function(data):
            return data

        test_function("test")

        # Should not create any captures
        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("test_function")
        assert len(captures) == 0

    def test_capture_ignored_function(self):
        """Test capture for ignored function patterns."""
        self.config.ignore_functions = ["ignored_*"]
        set_global_config(self.config)

        @capture_args()
        def ignored_function(data):
            return data

        ignored_function("test")

        # Should not create captures for ignored functions
        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("ignored_function")
        assert len(captures) == 0

    def test_async_function_capture(self):
        """Test capture for async functions."""
        @capture_args()
        async def async_function(data):
            await asyncio.sleep(0.01)
            return data.upper()

        async def run_test():
            result = await async_function("hello")
            assert result == "HELLO"

            # Verify capture
            args, kwargs = load_capture("async_function")
            assert args == ("hello",)

        asyncio.run(run_test())

    def test_capture_with_exception(self):
        """Test that capture works even when function raises exception."""
        @capture_args()
        def failing_function(data):
            if data == "fail":
                raise ValueError("Test error")
            return data

        # Call with success
        result = failing_function("success")
        assert result == "success"

        # Call with failure
        with pytest.raises(ValueError):
            failing_function("fail")

        # Both calls should be captured
        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("failing_function")
        assert len(captures) == 2

    def test_overwrite_behavior(self):
        """Test overwrite parameter behavior."""
        @capture_args(overwrite=False)
        def test_function(data):
            return data

        # First call
        test_function("first")
        storage = CaptureStorage(self.temp_dir)
        assert len(storage.list_captures("test_function")) == 1

        # Second call with overwrite=False should not create new capture
        test_function("second")
        captures = storage.list_captures("test_function")
        assert len(captures) == 1
        assert captures[0].args == ("first",)

    def test_custom_config(self):
        """Test capture with custom configuration."""
        custom_config = CaptureConfig()
        custom_config.default_retention = 5
        custom_config.ignore_args = ["custom_ignore"]

        @capture_args(config=custom_config)
        def test_function(data, custom_ignore=None):
            return data

        test_function("test", custom_ignore="secret")

        args, kwargs = load_capture("test_function")
        assert kwargs["custom_ignore"] == "<FILTERED:CUSTOM_IGNORE>"


class TestCaptureContext:
    """Test CaptureContext context manager."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = CaptureConfig()
        self.config.default_path = self.temp_dir
        set_global_config(self.config)

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_context_disable(self):
        """Test disabling capture in context."""
        @capture_args()
        def test_function(data):
            return data

        # Normal capture
        test_function("normal")

        # Disabled in context
        with CaptureContext(enabled=False):
            test_function("disabled")

        # Normal capture again
        test_function("normal_again")

        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("test_function")

        # Should have 2 captures (disabled one should be skipped)
        assert len(captures) == 2

    def test_context_custom_path(self):
        """Test custom path in context."""
        custom_path = str(Path(self.temp_dir) / "context_custom")

        @capture_args()
        def test_function(data):
            return data

        with CaptureContext(path=custom_path):
            test_function("context_data")

        # Check custom path
        custom_storage = CaptureStorage(custom_path)
        captures = custom_storage.list_captures("test_function")
        assert len(captures) == 1

        # Check default path should be empty
        default_storage = CaptureStorage(self.temp_dir)
        captures = default_storage.list_captures("test_function")
        assert len(captures) == 0


class TestConvenienceDecorators:
    """Test convenience decorator functions."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = CaptureConfig()
        self.config.default_path = self.temp_dir
        set_global_config(self.config)

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_disable_capture_decorator(self):
        """Test @disable_capture decorator."""
        @disable_capture()
        def test_function(data):
            return data

        test_function("test")

        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("test_function")
        assert len(captures) == 0

    def test_capture_once_decorator(self):
        """Test @capture_once decorator."""
        @capture_once()
        def test_function(data):
            return data

        # Multiple calls
        test_function("first")
        test_function("second")
        test_function("third")

        # Should only capture once
        storage = CaptureStorage(self.temp_dir)
        captures = storage.list_captures("test_function")
        assert len(captures) == 1
        assert captures[0].args == ("first",)

    def test_capture_minimal_decorator(self):
        """Test @capture_minimal decorator."""
        @capture_minimal()
        def test_function(data, large_object=None):
            return data

        test_function("test", large_object={"large": "data"})

        args, kwargs = load_capture("test_function")

        # Should capture type information instead of actual values
        assert isinstance(args[0], str) and "str" in args[0]
        assert isinstance(kwargs["large_object"], str) and "dict" in kwargs["large_object"]


class TestErrorHandling:
    """Test error handling in capture functionality."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = CaptureConfig()
        self.config.default_path = self.temp_dir
        set_global_config(self.config)

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_capture_with_unpickleable_args(self):
        """Test capture behavior with unpickleable arguments."""
        @capture_args()
        def test_function(func, data):
            return func(data)

        # Lambda function is not pickleable
        result = test_function(lambda x: x.upper(), "hello")
        assert result == "HELLO"

        # Function should still work despite capture failure
        # The capture may fail gracefully or use a placeholder

    def test_capture_with_large_args(self):
        """Test capture behavior with very large arguments."""
        @capture_args()
        def test_function(large_data):
            return len(large_data)

        # Create large data
        large_data = "x" * 1000000  # 1MB string

        result = test_function(large_data)
        assert result == 1000000

        # Function should still work
        # Capture system should handle large data appropriately


if __name__ == "__main__":
    pytest.main([__file__])