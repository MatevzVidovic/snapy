"""
Tests for configuration management.
"""

import os
import tempfile
from pathlib import Path
import pytest

from snapy.capture.config import CaptureConfig, get_global_config, set_global_config


class TestCaptureConfig:
    """Test CaptureConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = CaptureConfig()
        assert config.enabled is True
        assert config.default_path == "./snap_capture"
        assert config.default_retention == 2
        assert config.default_overwrite is False
        assert "password" in config.ignore_args
        assert "token" in config.ignore_args

    def test_env_variable_override(self):
        """Test configuration from environment variables."""
        # Set environment variables
        os.environ["SNAP_CAPTURE_ENABLED"] = "false"
        os.environ["SNAP_CAPTURE_DEFAULT_PATH"] = "./test_captures"
        os.environ["SNAP_CAPTURE_DEFAULT_RETENTION"] = "5"
        os.environ["SNAP_CAPTURE_IGNORE_ARGS"] = "secret,api_key"

        try:
            config = CaptureConfig()
            assert config.enabled is False
            assert config.default_path == "./test_captures"
            assert config.default_retention == 5
            assert "secret" in config.ignore_args
            assert "api_key" in config.ignore_args
        finally:
            # Clean up environment variables
            for key in ["SNAP_CAPTURE_ENABLED", "SNAP_CAPTURE_DEFAULT_PATH",
                       "SNAP_CAPTURE_DEFAULT_RETENTION", "SNAP_CAPTURE_IGNORE_ARGS"]:
                os.environ.pop(key, None)

    def test_parse_env_list(self):
        """Test parsing comma-separated environment variables."""
        result = CaptureConfig._parse_env_list("TEST_VAR", ["default1", "default2"])
        assert result == ["default1", "default2"]

        os.environ["TEST_VAR"] = "item1,item2,item3"
        try:
            result = CaptureConfig._parse_env_list("TEST_VAR")
            assert result == ["item1", "item2", "item3"]
        finally:
            os.environ.pop("TEST_VAR", None)

    def test_from_env_file(self):
        """Test loading configuration from .env file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("SNAP_CAPTURE_ENABLED=false\n")
            f.write("SNAP_CAPTURE_DEFAULT_PATH=./env_test\n")
            f.write("SNAP_CAPTURE_DEFAULT_RETENTION=3\n")
            env_file_path = f.name

        try:
            config = CaptureConfig.from_env_file(env_file_path)
            assert config.enabled is False
            assert config.default_path == "./env_test"
            assert config.default_retention == 3
        finally:
            os.unlink(env_file_path)
            # Clean up environment variables that might have been set
            for key in ["SNAP_CAPTURE_ENABLED", "SNAP_CAPTURE_DEFAULT_PATH",
                       "SNAP_CAPTURE_DEFAULT_RETENTION"]:
                os.environ.pop(key, None)

    def test_is_function_ignored(self):
        """Test function ignore patterns."""
        config = CaptureConfig()
        config.ignore_modules = ["test.*", "django.*"]
        config.ignore_functions = ["*secret*", "*password*"]

        assert config.is_function_ignored("get_password", "mymodule") is True
        assert config.is_function_ignored("normal_function", "test.module") is True
        assert config.is_function_ignored("normal_function", "mymodule") is False

    def test_is_arg_ignored(self):
        """Test argument ignore patterns."""
        config = CaptureConfig()
        config.ignore_args = ["password", "*token*", "secret"]

        assert config.is_arg_ignored("password") is True
        assert config.is_arg_ignored("access_token") is True
        assert config.is_arg_ignored("user_token") is True
        assert config.is_arg_ignored("username") is False

    def test_match_pattern(self):
        """Test pattern matching with wildcards."""
        assert CaptureConfig._match_pattern("test.*", "test.module") is True
        assert CaptureConfig._match_pattern("*password*", "get_password") is True
        assert CaptureConfig._match_pattern("exact", "exact") is True
        assert CaptureConfig._match_pattern("test.*", "other.module") is False

    def test_get_capture_path(self):
        """Test capture path creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config = CaptureConfig()
            config.default_path = temp_dir

            # Test default path
            path = config.get_capture_path()
            assert path == Path(temp_dir)
            assert path.exists()

            # Test custom path
            custom_path = str(Path(temp_dir) / "custom")
            path = config.get_capture_path(custom_path)
            assert path == Path(custom_path)
            assert path.exists()

    def test_should_capture(self):
        """Test capture decision logic."""
        config = CaptureConfig()
        config.enabled = True
        config.ignore_functions = ["ignored_*"]

        assert config.should_capture("normal_function", "mymodule") is True
        assert config.should_capture("ignored_function", "mymodule") is True  # partial match
        assert config.should_capture("ignored_test", "mymodule") is True  # partial match

        config.enabled = False
        assert config.should_capture("normal_function", "mymodule") is False

    def test_to_dict(self):
        """Test configuration serialization to dictionary."""
        config = CaptureConfig()
        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert "enabled" in config_dict
        assert "default_path" in config_dict
        assert "ignore_args" in config_dict


class TestGlobalConfig:
    """Test global configuration management."""

    def setup_method(self):
        """Setup for each test method."""
        # Reset global config
        from snapy.capture.config import _global_config
        snapy_capture.config._global_config = None

    def test_get_global_config(self):
        """Test getting global configuration."""
        config = get_global_config()
        assert isinstance(config, CaptureConfig)

        # Should return same instance on subsequent calls
        config2 = get_global_config()
        assert config is config2

    def test_set_global_config(self):
        """Test setting global configuration."""
        custom_config = CaptureConfig()
        custom_config.enabled = False

        set_global_config(custom_config)
        retrieved_config = get_global_config()

        assert retrieved_config is custom_config
        assert retrieved_config.enabled is False


if __name__ == "__main__":
    pytest.main([__file__])