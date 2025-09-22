"""
Configuration management for snap capture functionality.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class CaptureConfig:
    """
    Configuration class for snap capture functionality.

    Manages settings from environment variables, .env files, and explicit parameters.
    """

    # Default configuration values
    enabled: bool = field(default_factory=lambda: os.getenv("SNAP_CAPTURE_ENABLED", "true").lower() == "true")
    default_path: str = field(default_factory=lambda: os.getenv("SNAP_CAPTURE_DEFAULT_PATH", "./snap_capture"))
    default_retention: int = field(default_factory=lambda: int(os.getenv("SNAP_CAPTURE_DEFAULT_RETENTION", "2")))
    default_overwrite: bool = field(default_factory=lambda: os.getenv("SNAP_CAPTURE_DEFAULT_OVERWRITE", "false").lower() == "true")

    # Filtering configuration
    ignore_modules: List[str] = field(default_factory=lambda: CaptureConfig._parse_env_list("SNAP_CAPTURE_IGNORE_MODULES"))
    ignore_functions: List[str] = field(default_factory=lambda: CaptureConfig._parse_env_list("SNAP_CAPTURE_IGNORE_FUNCTIONS"))
    ignore_args: List[str] = field(default_factory=lambda: CaptureConfig._parse_env_list("SNAP_CAPTURE_IGNORE_ARGS",
                                                                                         ["password", "token", "secret", "key", "auth"]))

    # Production optimization
    production_mode: bool = field(default_factory=lambda: os.getenv("SNAP_CAPTURE_PRODUCTION_MODE", "false").lower() == "true")
    minimal_capture: bool = field(default_factory=lambda: os.getenv("SNAP_CAPTURE_MINIMAL", "false").lower() == "true")

    @staticmethod
    def _parse_env_list(env_var: str, default: Optional[List[str]] = None) -> List[str]:
        """Parse comma-separated environment variable into a list."""
        value = os.getenv(env_var)
        if value:
            return [item.strip() for item in value.split(",") if item.strip()]
        return default or []

    @classmethod
    def from_env_file(cls, env_file_path: Optional[str] = None) -> "CaptureConfig":
        """
        Create configuration from .env file.

        Args:
            env_file_path: Path to .env file. If None, looks for .env in current directory.

        Returns:
            CaptureConfig instance with values loaded from .env file
        """
        if env_file_path is None:
            env_file_path = ".env"

        env_path = Path(env_file_path)
        if env_path.exists():
            cls._load_env_file(env_path)

        return cls()

    @staticmethod
    def _load_env_file(env_path: Path) -> None:
        """Load environment variables from .env file."""
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ.setdefault(key, value)

    def is_function_ignored(self, function_name: str, module_name: str) -> bool:
        """
        Check if a function should be ignored based on configuration.

        Args:
            function_name: Name of the function
            module_name: Name of the module containing the function

        Returns:
            True if the function should be ignored, False otherwise
        """
        # Check module patterns
        for pattern in self.ignore_modules:
            if self._match_pattern(pattern, module_name):
                return True

        # Check function patterns
        for pattern in self.ignore_functions:
            if self._match_pattern(pattern, function_name):
                return True

        return False

    def is_arg_ignored(self, arg_name: str) -> bool:
        """
        Check if an argument should be ignored based on configuration.

        Args:
            arg_name: Name of the argument

        Returns:
            True if the argument should be ignored, False otherwise
        """
        for pattern in self.ignore_args:
            if self._match_pattern(pattern, arg_name):
                return True
        return False

    @staticmethod
    def _match_pattern(pattern: str, text: str) -> bool:
        """
        Match a pattern against text using wildcards.

        Args:
            pattern: Pattern with possible wildcards (*)
            text: Text to match against

        Returns:
            True if pattern matches, False otherwise
        """
        # Convert wildcard pattern to regex
        regex_pattern = pattern.replace("*", ".*")
        regex_pattern = f"^{regex_pattern}$"

        try:
            return bool(re.match(regex_pattern, text, re.IGNORECASE))
        except re.error:
            # If regex is invalid, fall back to simple string matching
            return pattern.lower() in text.lower()

    def get_capture_path(self, custom_path: Optional[str] = None) -> Path:
        """
        Get the capture path, with optional override.

        Args:
            custom_path: Custom path to use instead of default

        Returns:
            Path object for capture storage
        """
        path_str = custom_path or self.default_path
        path = Path(path_str)

        # Create directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)

        return path

    def should_capture(self, function_name: str, module_name: str) -> bool:
        """
        Determine if capturing should be performed for a given function.

        Args:
            function_name: Name of the function
            module_name: Name of the module

        Returns:
            True if capturing should be performed, False otherwise
        """
        if not self.enabled:
            return False

        if self.is_function_ignored(function_name, module_name):
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "enabled": self.enabled,
            "default_path": self.default_path,
            "default_retention": self.default_retention,
            "default_overwrite": self.default_overwrite,
            "ignore_modules": self.ignore_modules,
            "ignore_functions": self.ignore_functions,
            "ignore_args": self.ignore_args,
            "production_mode": self.production_mode,
            "minimal_capture": self.minimal_capture
        }


# Global configuration instance
_global_config: Optional[CaptureConfig] = None


def get_global_config() -> CaptureConfig:
    """
    Get the global configuration instance.

    Returns:
        Global CaptureConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = CaptureConfig.from_env_file()
    return _global_config


def set_global_config(config: CaptureConfig) -> None:
    """
    Set the global configuration instance.

    Args:
        config: CaptureConfig instance to set as global
    """
    global _global_config
    _global_config = config