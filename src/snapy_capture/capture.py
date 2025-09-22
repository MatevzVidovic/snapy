"""
Main capture decorator for function argument capture.
"""

import functools
import inspect
import asyncio
from collections import OrderedDict
from typing import Callable, Optional, List, Any, TypeVar, Union, Dict
from .config import CaptureConfig, get_global_config
from .storage import CaptureStorage
from .filters import ArgumentFilter

F = TypeVar('F', bound=Callable[..., Any])


def capture_args(
    path: Optional[str] = None,
    retention: Optional[int] = None,
    overwrite: Optional[bool] = None,
    ignore_args: Optional[List[str]] = None,
    config: Optional[CaptureConfig] = None,
    enabled: Optional[bool] = None
) -> Callable[[F], F]:
    """
    Decorator that captures function arguments for replay in tests.

    Args:
        path: Custom storage path (overrides config default)
        retention: Number of captures to retain (overrides config default)
        overwrite: Whether to overwrite existing captures (overrides config default)
        ignore_args: Additional argument names to ignore (extends config)
        config: Custom CaptureConfig instance (overrides global config)
        enabled: Override global enable/disable setting

    Returns:
        Decorated function that captures arguments when called

    Example:
        @capture_args(path="./my_captures", retention=3)
        def process_data(user_id, data, password=None):
            return {"processed": data, "user": user_id}

        # When called, arguments are automatically captured
        result = process_data("user123", {"key": "value"}, password="secret")
    """

    def decorator(func: F) -> F:
        # Get configuration
        effective_config = config or get_global_config()

        # Override config values if provided
        if ignore_args:
            # Create a copy of config with additional ignore patterns
            import copy
            effective_config = copy.deepcopy(effective_config)
            effective_config.ignore_args.extend(ignore_args)

        # Get function metadata
        function_name = func.__name__
        module_name = func.__module__ or ""

        # Check if this function should be captured
        capture_enabled = enabled if enabled is not None else effective_config.enabled
        if not capture_enabled or effective_config.is_function_ignored(function_name, module_name):
            # Return original function unchanged if disabled or ignored
            return func

        # Initialize storage and filter
        storage = CaptureStorage(effective_config.get_capture_path(path))
        arg_filter = ArgumentFilter(effective_config)

        # Handle both sync and async functions
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await _capture_and_call_async(
                    func, args, kwargs, function_name, module_name,
                    storage, arg_filter, effective_config, retention, overwrite
                )
            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                return _capture_and_call_sync(
                    func, args, kwargs, function_name, module_name,
                    storage, arg_filter, effective_config, retention, overwrite
                )
            return sync_wrapper

    return decorator


def _capture_and_call_sync(
    func: Callable,
    args: tuple,
    kwargs: dict,
    function_name: str,
    module_name: str,
    storage: CaptureStorage,
    arg_filter: ArgumentFilter,
    config: CaptureConfig,
    retention: Optional[int],
    overwrite: Optional[bool]
) -> Any:
    """Handle capture and execution for synchronous functions."""
    try:
        # Capture arguments before function execution
        _capture_arguments(
            func, args, kwargs, function_name, module_name,
            storage, arg_filter, config, retention, overwrite
        )
    except Exception as e:
        # Don't fail the original function if capture fails
        print(f"Warning: Argument capture failed for {function_name}: {e}")

    # Execute original function
    return func(*args, **kwargs)


async def _capture_and_call_async(
    func: Callable,
    args: tuple,
    kwargs: dict,
    function_name: str,
    module_name: str,
    storage: CaptureStorage,
    arg_filter: ArgumentFilter,
    config: CaptureConfig,
    retention: Optional[int],
    overwrite: Optional[bool]
) -> Any:
    """Handle capture and execution for asynchronous functions."""
    try:
        # Capture arguments before function execution
        _capture_arguments(
            func, args, kwargs, function_name, module_name,
            storage, arg_filter, config, retention, overwrite
        )
    except Exception as e:
        # Don't fail the original function if capture fails
        print(f"Warning: Argument capture failed for {function_name}: {e}")

    # Execute original function
    return await func(*args, **kwargs)


def _args_to_named_dict(func: Callable, args: tuple, kwargs: dict) -> OrderedDict[str, Any]:
    """
    Convert positional and keyword arguments to a named dictionary using function signature.

    Args:
        func: The function being called
        args: Positional arguments tuple
        kwargs: Keyword arguments dict

    Returns:
        OrderedDict mapping parameter names to values in signature order
    """
    try:
        # Get function signature
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Create ordered dict preserving parameter order
        named_args = OrderedDict()
        for param_name in sig.parameters.keys():
            if param_name in bound_args.arguments:
                named_args[param_name] = bound_args.arguments[param_name]

        return named_args

    except (TypeError, ValueError) as e:
        # Fallback: create basic mapping if signature binding fails
        print(f"Warning: Could not bind arguments to function signature: {e}")

        # Try to get parameter names from function
        try:
            param_names = list(inspect.signature(func).parameters.keys())
            named_args = OrderedDict()

            # Map positional args to parameter names
            for i, arg_value in enumerate(args):
                if i < len(param_names):
                    named_args[param_names[i]] = arg_value
                else:
                    # Extra positional args
                    named_args[f"*args[{i}]"] = arg_value

            # Add keyword arguments
            for key, value in kwargs.items():
                named_args[key] = value

            return named_args

        except Exception:
            # Ultimate fallback: just use indices for positional args
            named_args = OrderedDict()
            for i, arg_value in enumerate(args):
                named_args[f"arg_{i}"] = arg_value
            for key, value in kwargs.items():
                named_args[key] = value

            return named_args


def _capture_arguments(
    func: Callable,
    args: tuple,
    kwargs: dict,
    function_name: str,
    module_name: str,
    storage: CaptureStorage,
    arg_filter: ArgumentFilter,
    config: CaptureConfig,
    retention: Optional[int],
    overwrite: Optional[bool]
) -> None:
    """Capture function arguments with filtering and storage."""
    # Use config defaults if not specified
    effective_retention = retention if retention is not None else config.default_retention
    effective_overwrite = overwrite if overwrite is not None else config.default_overwrite

    # Convert args to named arguments using function signature
    all_args_dict = _args_to_named_dict(func, args, kwargs)

    # Filter arguments
    if arg_filter.should_capture_minimal():
        # Minimal capture for production
        filtered_args_dict = arg_filter.get_minimal_args_dict(all_args_dict)
    else:
        # Full capture with filtering
        filtered_args_dict = arg_filter.filter_args_dict(all_args_dict)

    # Save capture
    storage.save_capture(
        function_name=function_name,
        module_name=module_name,
        args_dict=filtered_args_dict,
        retention=effective_retention,
        overwrite=effective_overwrite
    )


class CaptureContext:
    """
    Context manager for temporarily enabling/disabling capture for a block of code.

    Example:
        with CaptureContext(enabled=False):
            # No captures will be made in this block
            some_decorated_function()

        with CaptureContext(path="./special_captures"):
            # Captures will use special path
            another_decorated_function()
    """

    def __init__(
        self,
        enabled: Optional[bool] = None,
        path: Optional[str] = None,
        retention: Optional[int] = None,
        config: Optional[CaptureConfig] = None
    ):
        """
        Initialize capture context.

        Args:
            enabled: Override global enabled setting
            path: Override storage path
            retention: Override retention setting
            config: Override global config
        """
        self.enabled = enabled
        self.path = path
        self.retention = retention
        self.config = config
        self._original_config = None

    def __enter__(self):
        """Enter context and apply overrides."""
        global _global_config
        from .config import _global_config

        # Store original config
        self._original_config = _global_config

        # Create modified config if needed
        if any([self.enabled is not None, self.path is not None,
                self.retention is not None, self.config is not None]):
            import copy

            if self.config:
                new_config = copy.deepcopy(self.config)
            else:
                new_config = copy.deepcopy(get_global_config())

            # Apply overrides
            if self.enabled is not None:
                new_config.enabled = self.enabled
            if self.path is not None:
                new_config.default_path = self.path
            if self.retention is not None:
                new_config.default_retention = self.retention

            # Set as global config
            from .config import set_global_config
            set_global_config(new_config)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original config."""
        if self._original_config is not None:
            from .config import set_global_config
            set_global_config(self._original_config)


# Convenience functions
def disable_capture():
    """
    Decorator to disable capture for a specific function.

    Example:
        @disable_capture()
        @capture_args()
        def my_function():
            pass  # This function won't capture arguments
    """
    return capture_args(enabled=False)


def capture_once(path: Optional[str] = None):
    """
    Decorator that captures arguments only once (overwrite=False).

    Args:
        path: Optional custom storage path

    Example:
        @capture_once()
        def expensive_function(large_data):
            pass  # Arguments captured only on first call
    """
    return capture_args(path=path, overwrite=False, retention=1)


def capture_minimal(path: Optional[str] = None):
    """
    Decorator that captures only minimal argument information.

    Args:
        path: Optional custom storage path

    Example:
        @capture_minimal()
        def production_function(sensitive_data):
            pass  # Only captures argument types, not values
    """
    import copy
    config = copy.deepcopy(get_global_config())
    config.minimal_capture = True
    return capture_args(path=path, config=config)