"""
Argument filtering functionality for snap capture.
"""

import copy
from typing import Any, Dict, List, Tuple, Set, Union
from collections import OrderedDict
from .config import CaptureConfig


class ArgumentFilter:
    """
    Filters function arguments based on configuration rules.

    Handles filtering of sensitive arguments and dictionary keys to prevent
    capturing passwords, tokens, and other sensitive data.
    """

    def __init__(self, config: CaptureConfig):
        """
        Initialize argument filter.

        Args:
            config: CaptureConfig instance with filtering rules
        """
        self.config = config
        self._sensitive_keys = self._build_sensitive_keys()

    def filter_args(self, args: Tuple[Any, ...], kwargs: Dict[str, Any]) -> Tuple[Tuple[Any, ...], Dict[str, Any]]:
        """
        Filter arguments and keyword arguments.

        Args:
            args: Positional arguments tuple
            kwargs: Keyword arguments dictionary

        Returns:
            Tuple of (filtered_args, filtered_kwargs)
        """
        # Filter kwargs by name
        filtered_kwargs = self._filter_kwargs_by_name(kwargs)

        # Deep filter dictionary values in both args and kwargs
        filtered_args = self._deep_filter_args(args)
        filtered_kwargs = self._deep_filter_dict(filtered_kwargs)

        return filtered_args, filtered_kwargs

    def filter_args_dict(self, args_dict: OrderedDict[str, Any]) -> OrderedDict[str, Any]:
        """
        Filter an ordered dictionary of named arguments.

        Args:
            args_dict: Ordered dictionary of argument names to values

        Returns:
            Filtered OrderedDict with sensitive arguments filtered
        """
        filtered_dict = OrderedDict()

        for arg_name, arg_value in args_dict.items():
            if self.config.is_arg_ignored(arg_name):
                # Replace with placeholder for sensitive args
                filtered_dict[arg_name] = f"<FILTERED:{arg_name.upper()}>"
            else:
                # Deep filter the value
                filtered_dict[arg_name] = self._deep_filter_value(arg_value)

        return filtered_dict

    def _filter_kwargs_by_name(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter kwargs by argument name patterns.

        Args:
            kwargs: Original keyword arguments

        Returns:
            Filtered keyword arguments dictionary
        """
        filtered = {}
        for key, value in kwargs.items():
            if not self.config.is_arg_ignored(key):
                filtered[key] = value
            else:
                # Replace with placeholder for sensitive args
                filtered[key] = f"<FILTERED:{key.upper()}>"

        return filtered

    def _deep_filter_args(self, args: Tuple[Any, ...]) -> Tuple[Any, ...]:
        """
        Deep filter positional arguments.

        Args:
            args: Original positional arguments

        Returns:
            Filtered positional arguments
        """
        filtered_args = []
        for arg in args:
            filtered_arg = self._deep_filter_value(arg)
            filtered_args.append(filtered_arg)

        return tuple(filtered_args)

    def _deep_filter_dict(self, obj: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep filter dictionary, including nested structures.

        Args:
            obj: Dictionary to filter

        Returns:
            Filtered dictionary
        """
        if not isinstance(obj, dict):
            return obj

        filtered = {}
        for key, value in obj.items():
            if self._is_sensitive_key(key):
                filtered[key] = f"<FILTERED:{key.upper()}>"
            else:
                filtered[key] = self._deep_filter_value(value)

        return filtered

    def _deep_filter_value(self, value: Any) -> Any:
        """
        Recursively filter a value of any type.

        Args:
            value: Value to filter

        Returns:
            Filtered value
        """
        if isinstance(value, dict):
            return self._deep_filter_dict(value)
        elif isinstance(value, (list, tuple)):
            return self._deep_filter_sequence(value)
        elif isinstance(value, set):
            return self._deep_filter_set(value)
        else:
            # For primitive types, check if the string representation contains sensitive data
            return self._filter_string_value(value)

    def _deep_filter_sequence(self, seq: Union[List, Tuple]) -> Union[List, Tuple]:
        """
        Deep filter list or tuple.

        Args:
            seq: Sequence to filter

        Returns:
            Filtered sequence of the same type
        """
        filtered_items = [self._deep_filter_value(item) for item in seq]

        if isinstance(seq, tuple):
            return tuple(filtered_items)
        else:
            return filtered_items

    def _deep_filter_set(self, s: Set) -> Set:
        """
        Deep filter set.

        Args:
            s: Set to filter

        Returns:
            Filtered set
        """
        return {self._deep_filter_value(item) for item in s}

    def _filter_string_value(self, value: Any) -> Any:
        """
        Filter string values that might contain sensitive data.

        Args:
            value: Value to check and potentially filter

        Returns:
            Original value or filtered placeholder
        """
        if not isinstance(value, str):
            return value

        # Check if string value looks like sensitive data
        value_lower = value.lower()
        for sensitive_pattern in self._sensitive_keys:
            if sensitive_pattern in value_lower and len(value) > 10:
                # If it's a long string containing sensitive keywords, filter it
                return f"<FILTERED:SENSITIVE_STRING>"

        return value

    def _is_sensitive_key(self, key: str) -> bool:
        """
        Check if a key is considered sensitive.

        Args:
            key: Key name to check

        Returns:
            True if the key should be filtered
        """
        if self.config.is_arg_ignored(key):
            return True

        key_lower = key.lower()
        return any(pattern in key_lower for pattern in self._sensitive_keys)

    def _build_sensitive_keys(self) -> List[str]:
        """
        Build list of sensitive key patterns.

        Returns:
            List of lowercase sensitive patterns
        """
        # Default sensitive patterns
        patterns = [
            "password", "passwd", "pwd",
            "token", "access_token", "refresh_token", "auth_token",
            "secret", "api_secret", "client_secret",
            "key", "api_key", "private_key", "public_key",
            "auth", "authorization",
            "credential", "creds",
            "session", "sessionid",
            "cookie", "cookies",
            "hash", "salt",
            "pin", "otp",
            "signature", "sign"
        ]

        # Add configured ignore patterns
        for pattern in self.config.ignore_args:
            # Remove wildcards for substring matching
            clean_pattern = pattern.replace("*", "").lower()
            if clean_pattern and clean_pattern not in patterns:
                patterns.append(clean_pattern)

        return patterns

    def should_capture_minimal(self) -> bool:
        """
        Check if only minimal capture should be performed.

        Returns:
            True if minimal capture mode is enabled
        """
        return self.config.minimal_capture or self.config.production_mode

    def get_minimal_args(
        self,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any]
    ) -> Tuple[Tuple[str, ...], Dict[str, str]]:
        """
        Get minimal representation of arguments for production use.

        Args:
            args: Original positional arguments
            kwargs: Original keyword arguments

        Returns:
            Tuple of (minimal_args, minimal_kwargs) with type information only
        """
        minimal_args = tuple(type(arg).__name__ for arg in args)
        minimal_kwargs = {key: type(value).__name__ for key, value in kwargs.items()
                         if not self.config.is_arg_ignored(key)}

        return minimal_args, minimal_kwargs

    def get_minimal_args_dict(self, args_dict: OrderedDict[str, Any]) -> OrderedDict[str, str]:
        """
        Get minimal representation of arguments dictionary for production use.

        Args:
            args_dict: Original ordered dictionary of arguments

        Returns:
            OrderedDict with type information only, filtered for sensitive args
        """
        minimal_dict = OrderedDict()

        for arg_name, arg_value in args_dict.items():
            if self.config.is_arg_ignored(arg_name):
                minimal_dict[arg_name] = f"<FILTERED:{arg_name.upper()}>"
            else:
                minimal_dict[arg_name] = type(arg_value).__name__

        return minimal_dict

    def create_filtered_copy(self, obj: Any) -> Any:
        """
        Create a deep copy of an object with filtering applied.

        Args:
            obj: Object to copy and filter

        Returns:
            Deep copy with sensitive data filtered
        """
        try:
            # Create deep copy first
            obj_copy = copy.deepcopy(obj)
            # Then apply filtering
            return self._deep_filter_value(obj_copy)
        except Exception:
            # If deep copy fails, return type information
            return f"<UNSERIALIZABLE:{type(obj).__name__}>"