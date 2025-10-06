"""
Tests for storage functionality.
"""

import tempfile
import os
from pathlib import Path
from datetime import datetime
import pytest

from snapy.capture.storage import CaptureStorage, CaptureMetadata, CapturedCall


class TestCaptureStorage:
    """Test CaptureStorage class."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = CaptureStorage(self.temp_dir)

    def teardown_method(self):
        """Cleanup after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init(self):
        """Test storage initialization."""
        assert self.storage.base_path == Path(self.temp_dir)
        assert self.storage.base_path.exists()

    def test_save_capture(self):
        """Test saving a function capture."""
        args = ("arg1", "arg2")
        kwargs = {"key1": "value1", "key2": "value2"}

        file_path = self.storage.save_capture(
            function_name="test_function",
            module_name="test_module",
            args=args,
            kwargs=kwargs
        )

        assert os.path.exists(file_path)
        assert "test_function" in file_path
        assert file_path.endswith(".pkl")

    def test_load_capture(self):
        """Test loading a capture from file."""
        args = ("arg1", "arg2")
        kwargs = {"key1": "value1"}

        # Save a capture
        file_path = self.storage.save_capture(
            function_name="test_function",
            module_name="test_module",
            args=args,
            kwargs=kwargs
        )

        # Load the capture
        capture = self.storage.load_capture(file_path)

        assert capture is not None
        assert capture.args == args
        assert capture.kwargs == kwargs
        assert capture.metadata.function_name == "test_function"
        assert capture.metadata.module_name == "test_module"

    def test_load_nonexistent_capture(self):
        """Test loading a non-existent capture."""
        capture = self.storage.load_capture("/nonexistent/path.pkl")
        assert capture is None

    def test_load_latest_capture(self):
        """Test loading the most recent capture."""
        # Save multiple captures
        self.storage.save_capture("test_func", "test_mod", ("old",), {})
        self.storage.save_capture("test_func", "test_mod", ("new",), {})

        # Load latest
        capture = self.storage.load_latest_capture("test_func")

        assert capture is not None
        assert capture.args == ("new",)

    def test_load_capture_by_index(self):
        """Test loading capture by index."""
        # Save multiple captures
        self.storage.save_capture("test_func", "test_mod", ("first",), {})
        self.storage.save_capture("test_func", "test_mod", ("second",), {})

        # Load by index (0 = most recent)
        capture_0 = self.storage.load_capture_by_index("test_func", 0)
        capture_1 = self.storage.load_capture_by_index("test_func", 1)

        assert capture_0.args == ("second",)
        assert capture_1.args == ("first",)

        # Test invalid index
        capture_invalid = self.storage.load_capture_by_index("test_func", 10)
        assert capture_invalid is None

    def test_list_captures(self):
        """Test listing all captures for a function."""
        # Save multiple captures
        self.storage.save_capture("test_func", "test_mod", ("first",), {})
        self.storage.save_capture("test_func", "test_mod", ("second",), {})

        captures = self.storage.list_captures("test_func")

        assert len(captures) == 2
        # Should be sorted by timestamp, newest first
        assert captures[0].args == ("second",)
        assert captures[1].args == ("first",)

    def test_list_all_functions(self):
        """Test listing all functions with captures."""
        self.storage.save_capture("func1", "mod1", (), {})
        self.storage.save_capture("func2", "mod2", (), {})
        self.storage.save_capture("func1", "mod1", (), {})  # Another capture for func1

        functions = self.storage.list_all_functions()

        assert "func1" in functions
        assert "func2" in functions
        assert len(functions) == 2

    def test_delete_captures(self):
        """Test deleting all captures for a function."""
        # Save multiple captures
        self.storage.save_capture("test_func", "test_mod", ("arg1",), {})
        self.storage.save_capture("test_func", "test_mod", ("arg2",), {})
        self.storage.save_capture("other_func", "test_mod", ("arg3",), {})

        # Delete captures for test_func
        deleted_count = self.storage.delete_captures("test_func")

        assert deleted_count == 2
        assert len(self.storage.list_captures("test_func")) == 0
        assert len(self.storage.list_captures("other_func")) == 1

    def test_retention_policy(self):
        """Test automatic cleanup based on retention policy."""
        # Save multiple captures with retention=2
        self.storage.save_capture("test_func", "test_mod", ("1",), {}, retention=2)
        self.storage.save_capture("test_func", "test_mod", ("2",), {}, retention=2)
        self.storage.save_capture("test_func", "test_mod", ("3",), {}, retention=2)

        captures = self.storage.list_captures("test_func")

        # Should only keep 2 most recent
        assert len(captures) == 2
        assert captures[0].args == ("3",)
        assert captures[1].args == ("2",)

    def test_overwrite_policy(self):
        """Test overwrite behavior."""
        # Save with overwrite=False (default)
        file1 = self.storage.save_capture("test_func", "test_mod", ("old",), {}, overwrite=False)
        file2 = self.storage.save_capture("test_func", "test_mod", ("new",), {}, overwrite=False)

        # Should not create new file if overwrite=False and captures exist
        assert file1 == file2

        # Clear captures and test overwrite=True
        self.storage.delete_captures("test_func")
        file3 = self.storage.save_capture("test_func", "test_mod", ("first",), {}, overwrite=True)
        file4 = self.storage.save_capture("test_func", "test_mod", ("second",), {}, overwrite=True)

        # Should create new file when overwrite=True
        assert file3 != file4

    def test_cleanup_all_captures(self):
        """Test cleaning up all captures across functions."""
        # Create multiple captures for different functions
        for i in range(5):
            self.storage.save_capture("func1", "mod", (f"arg{i}",), {})
        for i in range(3):
            self.storage.save_capture("func2", "mod", (f"arg{i}",), {})

        # Cleanup with retention=2
        deleted_count = self.storage.cleanup_all_captures(retention=2)

        assert deleted_count == 4  # 3 from func1 + 1 from func2
        assert len(self.storage.list_captures("func1")) == 2
        assert len(self.storage.list_captures("func2")) == 2

    def test_get_storage_stats(self):
        """Test getting storage statistics."""
        # Create some captures
        self.storage.save_capture("func1", "mod1", ("data",), {})
        self.storage.save_capture("func2", "mod2", ("more_data",), {})

        stats = self.storage.get_storage_stats()

        assert stats["total_functions"] == 2
        assert stats["total_files"] == 2
        assert stats["total_size_bytes"] > 0
        assert "func1" in stats["function_stats"]
        assert "func2" in stats["function_stats"]

    def test_thread_safety(self):
        """Test thread-safe operations."""
        import threading
        import time

        def save_captures():
            for i in range(10):
                self.storage.save_capture(f"func{i % 2}", "mod", (f"arg{i}",), {})
                time.sleep(0.001)  # Small delay to increase chance of race conditions

        # Run multiple threads simultaneously
        threads = [threading.Thread(target=save_captures) for _ in range(3)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Check that all captures were saved
        total_captures = sum(
            len(self.storage.list_captures(func))
            for func in self.storage.list_all_functions()
        )
        assert total_captures == 30  # 3 threads * 10 captures each


class TestCaptureMetadata:
    """Test CaptureMetadata class."""

    def test_metadata_creation(self):
        """Test creating metadata."""
        timestamp = datetime.now()
        metadata = CaptureMetadata(
            function_name="test_func",
            module_name="test_mod",
            timestamp=timestamp,
            args_count=2,
            kwargs_count=1,
            file_path="/path/to/file.pkl"
        )

        assert metadata.function_name == "test_func"
        assert metadata.module_name == "test_mod"
        assert metadata.timestamp == timestamp
        assert metadata.args_count == 2
        assert metadata.kwargs_count == 1
        assert metadata.file_path == "/path/to/file.pkl"


class TestCapturedCall:
    """Test CapturedCall class."""

    def test_captured_call_creation(self):
        """Test creating a captured call."""
        metadata = CaptureMetadata(
            function_name="test_func",
            module_name="test_mod",
            timestamp=datetime.now(),
            args_count=1,
            kwargs_count=1,
            file_path="/path/to/file.pkl"
        )

        args = ("arg1",)
        kwargs = {"key1": "value1"}

        captured_call = CapturedCall(
            metadata=metadata,
            args=args,
            kwargs=kwargs
        )

        assert captured_call.metadata == metadata
        assert captured_call.args == args
        assert captured_call.kwargs == kwargs


if __name__ == "__main__":
    pytest.main([__file__])