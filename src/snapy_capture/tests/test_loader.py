"""
Tests for loader functionality.
"""

import tempfile
import shutil
import pytest

from snapy_capture.loader import CaptureLoader, load_capture, load_all_captures, has_capture, CaptureFixture
from snapy_capture.storage import CaptureStorage
from snapy_capture.config import CaptureConfig, set_global_config


class TestCaptureLoader:
    """Test CaptureLoader class."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = CaptureStorage(self.temp_dir)
        self.loader = CaptureLoader(self.temp_dir)

        # Set up global config
        config = CaptureConfig()
        config.default_path = self.temp_dir
        set_global_config(config)

        # Create test captures
        self.storage.save_capture("func1", "mod1", ("arg1", "arg2"), {"key1": "value1"})
        self.storage.save_capture("func1", "mod1", ("arg3", "arg4"), {"key2": "value2"})
        self.storage.save_capture("func2", "mod2", ("other_arg",), {})

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_latest(self):
        """Test loading latest capture."""
        args, kwargs = self.loader.load_latest("func1")

        assert args == ("arg3", "arg4")  # Most recent
        assert kwargs == {"key2": "value2"}

    def test_load_latest_nonexistent(self):
        """Test loading latest capture for non-existent function."""
        result = self.loader.load_latest("nonexistent")
        assert result is None

    def test_load_by_index(self):
        """Test loading capture by index."""
        # Load most recent (index 0)
        args, kwargs = self.loader.load_by_index("func1", 0)
        assert args == ("arg3", "arg4")

        # Load older (index 1)
        args, kwargs = self.loader.load_by_index("func1", 1)
        assert args == ("arg1", "arg2")

        # Invalid index
        result = self.loader.load_by_index("func1", 10)
        assert result is None

    def test_load_all(self):
        """Test loading all captures for a function."""
        all_captures = self.loader.load_all("func1")

        assert len(all_captures) == 2
        # Should be sorted newest first
        assert all_captures[0][0] == ("arg3", "arg4")
        assert all_captures[1][0] == ("arg1", "arg2")

    def test_load_capture_object(self):
        """Test loading full capture object."""
        capture = self.loader.load_capture_object("func1")

        assert capture is not None
        assert capture.args == ("arg3", "arg4")
        assert capture.kwargs == {"key2": "value2"}
        assert capture.metadata.function_name == "func1"
        assert capture.metadata.module_name == "mod1"

    def test_list_functions(self):
        """Test listing all functions with captures."""
        functions = self.loader.list_functions()

        assert "func1" in functions
        assert "func2" in functions
        assert len(functions) == 2

    def test_has_captures(self):
        """Test checking if function has captures."""
        assert self.loader.has_captures("func1") is True
        assert self.loader.has_captures("func2") is True
        assert self.loader.has_captures("nonexistent") is False

    def test_get_capture_count(self):
        """Test getting capture count for function."""
        assert self.loader.get_capture_count("func1") == 2
        assert self.loader.get_capture_count("func2") == 1
        assert self.loader.get_capture_count("nonexistent") == 0

    def test_delete_captures(self):
        """Test deleting captures for function."""
        deleted_count = self.loader.delete_captures("func1")

        assert deleted_count == 2
        assert self.loader.has_captures("func1") is False
        assert self.loader.has_captures("func2") is True  # Other function unaffected

    def test_get_storage_stats(self):
        """Test getting storage statistics."""
        stats = self.loader.get_storage_stats()

        assert stats["total_functions"] == 2
        assert stats["total_files"] == 3
        assert "func1" in stats["function_stats"]
        assert "func2" in stats["function_stats"]


class TestConvenienceFunctions:
    """Test convenience functions."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = CaptureStorage(self.temp_dir)

        # Set up global config
        config = CaptureConfig()
        config.default_path = self.temp_dir
        set_global_config(config)

        # Create test capture
        self.storage.save_capture("test_func", "test_mod", ("test_arg",), {"test_key": "test_value"})

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_capture_latest(self):
        """Test load_capture convenience function with latest=True."""
        args, kwargs = load_capture("test_func", latest=True)

        assert args == ("test_arg",)
        assert kwargs == {"test_key": "test_value"}

    def test_load_capture_by_index(self):
        """Test load_capture convenience function with index."""
        args, kwargs = load_capture("test_func", index=0, latest=False)

        assert args == ("test_arg",)
        assert kwargs == {"test_key": "test_value"}

    def test_load_capture_custom_path(self):
        """Test load_capture with custom path."""
        args, kwargs = load_capture("test_func", path=self.temp_dir)

        assert args == ("test_arg",)
        assert kwargs == {"test_key": "test_value"}

    def test_load_capture_nonexistent(self):
        """Test load_capture for non-existent function."""
        result = load_capture("nonexistent")
        assert result is None

    def test_load_all_captures(self):
        """Test load_all_captures convenience function."""
        all_captures = load_all_captures("test_func")

        assert len(all_captures) == 1
        args, kwargs = all_captures[0]
        assert args == ("test_arg",)
        assert kwargs == {"test_key": "test_value"}

    def test_load_all_captures_custom_path(self):
        """Test load_all_captures with custom path."""
        all_captures = load_all_captures("test_func", path=self.temp_dir)

        assert len(all_captures) == 1

    def test_has_capture_function(self):
        """Test has_capture convenience function."""
        assert has_capture("test_func") is True
        assert has_capture("nonexistent") is False

    def test_has_capture_custom_path(self):
        """Test has_capture with custom path."""
        assert has_capture("test_func", path=self.temp_dir) is True


class TestCaptureFixture:
    """Test CaptureFixture for pytest integration."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = CaptureStorage(self.temp_dir)
        self.fixture = CaptureFixture(self.temp_dir)

        # Create test captures
        self.storage.save_capture("test_func", "test_mod", ("arg1",), {"key1": "value1"})
        self.storage.save_capture("test_func", "test_mod", ("arg2",), {"key2": "value2"})

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_fixture_call_latest(self):
        """Test calling fixture with latest=True."""
        fixture_func = self.fixture("test_func", latest=True)
        args, kwargs = fixture_func()

        assert args == ("arg2",)  # Most recent
        assert kwargs == {"key2": "value2"}

    def test_fixture_call_by_index(self):
        """Test calling fixture with specific index."""
        fixture_func = self.fixture("test_func", index=1, latest=False)
        args, kwargs = fixture_func()

        assert args == ("arg1",)  # Older capture
        assert kwargs == {"key1": "value1"}

    def test_fixture_nonexistent_function(self):
        """Test fixture with non-existent function."""
        fixture_func = self.fixture("nonexistent")

        with pytest.raises(ValueError, match="No captures found"):
            fixture_func()

    def test_create_parametrized_fixture(self):
        """Test creating parametrized fixture."""
        params = self.fixture.create_parametrized_fixture("test_func")

        assert len(params) == 2
        # Should be sorted newest first
        assert params[0][0] == ("arg2",)
        assert params[1][0] == ("arg1",)

    def test_create_parametrized_fixture_nonexistent(self):
        """Test creating parametrized fixture for non-existent function."""
        with pytest.raises(ValueError, match="No captures found"):
            self.fixture.create_parametrized_fixture("nonexistent")


class TestLoaderIntegration:
    """Test loader integration with actual captured functions."""

    def setup_method(self):
        """Setup for each test method."""
        self.temp_dir = tempfile.mkdtemp()
        config = CaptureConfig()
        config.default_path = self.temp_dir
        set_global_config(config)

    def teardown_method(self):
        """Cleanup after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_end_to_end_capture_and_load(self):
        """Test complete capture and load workflow."""
        from snapy_capture.capture import capture_args

        @capture_args()
        def example_function(x, y, operation="add"):
            if operation == "add":
                return x + y
            elif operation == "multiply":
                return x * y
            return None

        # Call function to create capture
        result1 = example_function(5, 3, operation="add")
        result2 = example_function(4, 6, operation="multiply")

        assert result1 == 8
        assert result2 == 24

        # Load captures and replay
        loader = CaptureLoader(self.temp_dir)

        # Test latest capture
        args, kwargs = loader.load_latest("example_function")
        replayed_result = example_function(*args, **kwargs)
        assert replayed_result == 24

        # Test all captures
        all_captures = loader.load_all("example_function")
        assert len(all_captures) == 2

        results = []
        for args, kwargs in all_captures:
            results.append(example_function(*args, **kwargs))

        assert 24 in results  # multiply result
        assert 8 in results   # add result

    def test_loader_with_default_path(self):
        """Test loader using default path from global config."""
        loader = CaptureLoader()  # No path specified, should use global config

        # Should work even with empty captures
        functions = loader.list_functions()
        assert isinstance(functions, list)


if __name__ == "__main__":
    pytest.main([__file__])