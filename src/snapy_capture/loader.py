"""
Loader utilities for accessing captured function arguments in tests.
"""

from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
from collections import OrderedDict
import inspect
from .storage import CaptureStorage, CapturedCall
from .config import get_global_config


class CaptureLoader:
    """
    Utility class for loading captured function arguments in tests.

    Provides convenient methods to access captured arguments for test replay.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize capture loader.

        Args:
            base_path: Base path for captures. If None, uses global config default.
        """
        config = get_global_config()
        if base_path is None:
            base_path = config.default_path

        self.storage = CaptureStorage(base_path)

    def load_latest(self, function_name: str) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
        """
        Load the most recent captured arguments for a function.

        Args:
            function_name: Name of the function

        Returns:
            Tuple of (args, kwargs) or None if no captures found

        Example:
            loader = CaptureLoader()
            args, kwargs = loader.load_latest("process_data")
            result = process_data(*args, **kwargs)
        """
        capture = self.storage.load_latest_capture(function_name)
        if capture:
            return capture.args, capture.kwargs
        return None

    def load_latest_dict(self, function_name: str) -> Optional[OrderedDict[str, Any]]:
        """
        Load the most recent captured arguments as an ordered dictionary.

        Args:
            function_name: Name of the function

        Returns:
            OrderedDict mapping parameter names to values, or None if no captures found

        Example:
            loader = CaptureLoader()
            args_dict = loader.load_latest_dict("process_data")
            if args_dict:
                # Use as positional args
                result = process_data(*args_dict.values())
                # Or use specific arguments
                result = process_data(args_dict['user_id'], args_dict['data'])
                # Or exclude some args
                filtered_args = {k: v for k, v in args_dict.items() if k != 'large_arg'}
                result = process_data(**filtered_args)
        """
        capture = self.storage.load_latest_capture(function_name)
        if capture:
            return capture.args_dict
        return None

    def load_by_index(
        self,
        function_name: str,
        index: int = 0
    ) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
        """
        Load captured arguments by index (0 = most recent).

        Args:
            function_name: Name of the function
            index: Index of the capture (0-based, 0 = most recent)

        Returns:
            Tuple of (args, kwargs) or None if capture not found

        Example:
            loader = CaptureLoader()
            # Get second most recent capture
            args, kwargs = loader.load_by_index("process_data", 1)
        """
        capture = self.storage.load_capture_by_index(function_name, index)
        if capture:
            return capture.args, capture.kwargs
        return None

    def load_by_index_dict(self, function_name: str, index: int = 0) -> Optional[OrderedDict[str, Any]]:
        """
        Load captured arguments by index as an ordered dictionary.

        Args:
            function_name: Name of the function
            index: Index of the capture (0-based, 0 = most recent)

        Returns:
            OrderedDict mapping parameter names to values, or None if not found

        Example:
            loader = CaptureLoader()
            args_dict = loader.load_by_index_dict("process_data", 1)
            if args_dict:
                # Exclude large arguments
                filtered = {k: v for k, v in args_dict.items() if k != 'large_model'}
                result = process_data(**filtered)
        """
        capture = self.storage.load_capture_by_index(function_name, index)
        if capture:
            return capture.args_dict
        return None

    def load_all(self, function_name: str) -> List[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
        """
        Load all captured arguments for a function.

        Args:
            function_name: Name of the function

        Returns:
            List of (args, kwargs) tuples, sorted by timestamp (newest first)

        Example:
            loader = CaptureLoader()
            all_captures = loader.load_all("process_data")
            for args, kwargs in all_captures:
                result = process_data(*args, **kwargs)
        """
        captures = self.storage.list_captures(function_name)
        return [(capture.args, capture.kwargs) for capture in captures]

    def load_all_dict(self, function_name: str) -> List[OrderedDict[str, Any]]:
        """
        Load all captured arguments as ordered dictionaries.

        Args:
            function_name: Name of the function

        Returns:
            List of OrderedDict objects, sorted by timestamp (newest first)

        Example:
            loader = CaptureLoader()
            all_captures = loader.load_all_dict("process_data")
            for args_dict in all_captures:
                # Filter out large arguments for this test
                filtered = {k: v for k, v in args_dict.items() if k != 'large_data'}
                result = process_data(**filtered)
        """
        captures = self.storage.list_captures(function_name)
        return [capture.args_dict for capture in captures]

    def load_capture_object(self, function_name: str, index: int = 0) -> Optional[CapturedCall]:
        """
        Load full capture object including metadata.

        Args:
            function_name: Name of the function
            index: Index of the capture (0-based, 0 = most recent)

        Returns:
            CapturedCall object or None if not found

        Example:
            loader = CaptureLoader()
            capture = loader.load_capture_object("process_data")
            print(f"Captured at: {capture.metadata.timestamp}")
            result = process_data(*capture.args, **capture.kwargs)
        """
        return self.storage.load_capture_by_index(function_name, index)

    def list_functions(self) -> List[str]:
        """
        List all functions that have captures.

        Returns:
            List of function names with stored captures

        Example:
            loader = CaptureLoader()
            functions = loader.list_functions()
            print(f"Functions with captures: {functions}")
        """
        return self.storage.list_all_functions()

    def has_captures(self, function_name: str) -> bool:
        """
        Check if a function has any captures.

        Args:
            function_name: Name of the function

        Returns:
            True if captures exist, False otherwise

        Example:
            loader = CaptureLoader()
            if loader.has_captures("process_data"):
                args, kwargs = loader.load_latest("process_data")
        """
        return bool(self.storage.list_captures(function_name))

    def get_capture_count(self, function_name: str) -> int:
        """
        Get the number of captures for a function.

        Args:
            function_name: Name of the function

        Returns:
            Number of captures available

        Example:
            loader = CaptureLoader()
            count = loader.get_capture_count("process_data")
            print(f"Found {count} captures")
        """
        return len(self.storage.list_captures(function_name))

    def delete_captures(self, function_name: str) -> int:
        """
        Delete all captures for a function.

        Args:
            function_name: Name of the function

        Returns:
            Number of files deleted

        Example:
            loader = CaptureLoader()
            deleted = loader.delete_captures("old_function")
            print(f"Deleted {deleted} capture files")
        """
        return self.storage.delete_captures(function_name)

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage statistics

        Example:
            loader = CaptureLoader()
            stats = loader.get_storage_stats()
            print(f"Total captures: {stats['total_files']}")
        """
        return self.storage.get_storage_stats()


# Convenience functions for common usage patterns

def load_capture(
    function_name: str,
    index: int = 0,
    path: Optional[str] = None,
    latest: bool = True
) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
    """
    Convenience function to load captured arguments.

    Args:
        function_name: Name of the function
        index: Index of the capture (ignored if latest=True)
        path: Custom capture path
        latest: If True, loads latest capture (ignores index)

    Returns:
        Tuple of (args, kwargs) or None if not found

    Example:
        # Load latest capture
        args, kwargs = load_capture("process_data")

        # Load specific capture
        args, kwargs = load_capture("process_data", index=1, latest=False)
    """
    loader = CaptureLoader(path)
    if latest:
        return loader.load_latest(function_name)
    else:
        return loader.load_by_index(function_name, index)


def load_capture_dict(
    function_name: str,
    index: int = 0,
    path: Optional[str] = None,
    latest: bool = True
) -> Optional[OrderedDict[str, Any]]:
    """
    Convenience function to load captured arguments as an ordered dictionary.

    Args:
        function_name: Name of the function
        index: Index of the capture (ignored if latest=True)
        path: Custom capture path
        latest: If True, loads latest capture (ignores index)

    Returns:
        OrderedDict mapping parameter names to values, or None if not found

    Example:
        # Load latest capture
        args_dict = load_capture_dict("process_data")
        if args_dict:
            # Use as positional args
            result = process_data(*args_dict.values())
            # Or filter out large args
            filtered = {k: v for k, v in args_dict.items() if k != 'large_model'}
            result = process_data(**filtered)
    """
    loader = CaptureLoader(path)
    if latest:
        return loader.load_latest_dict(function_name)
    else:
        return loader.load_by_index_dict(function_name, index)


def load_all_captures(
    function_name: str,
    path: Optional[str] = None
) -> List[Tuple[Tuple[Any, ...], Dict[str, Any]]]:
    """
    Convenience function to load all captures for a function.

    Args:
        function_name: Name of the function
        path: Custom capture path

    Returns:
        List of (args, kwargs) tuples

    Example:
        all_captures = load_all_captures("process_data")
        for args, kwargs in all_captures:
            test_process_data(*args, **kwargs)
    """
    loader = CaptureLoader(path)
    return loader.load_all(function_name)


def has_capture(function_name: str, path: Optional[str] = None) -> bool:
    """
    Convenience function to check if captures exist.

    Args:
        function_name: Name of the function
        path: Custom capture path

    Returns:
        True if captures exist

    Example:
        if has_capture("process_data"):
            args, kwargs = load_capture("process_data")
        else:
            args, kwargs = create_test_args()
    """
    loader = CaptureLoader(path)
    return loader.has_captures(function_name)


class CaptureFixture:
    """
    Pytest fixture helper for working with captures.

    Can be used to create pytest fixtures that automatically load captures.
    """

    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize capture fixture.

        Args:
            base_path: Base path for captures
        """
        self.loader = CaptureLoader(base_path)

    def __call__(self, function_name: str, index: int = 0, latest: bool = True):
        """
        Create a fixture that loads captures for a specific function.

        Args:
            function_name: Name of the function
            index: Index of the capture
            latest: Whether to load latest capture

        Returns:
            Function that can be used as pytest fixture

        Example:
            # In conftest.py
            capture_fixture = CaptureFixture()

            @pytest.fixture
            def process_data_args():
                return capture_fixture("process_data")

            # In test file
            def test_process_data(process_data_args):
                args, kwargs = process_data_args
                result = process_data(*args, **kwargs)
                assert result is not None
        """
        def fixture():
            if latest:
                result = self.loader.load_latest(function_name)
            else:
                result = self.loader.load_by_index(function_name, index)

            if result is None:
                raise ValueError(f"No captures found for function '{function_name}'")
            return result

        return fixture

    def create_parametrized_fixture(self, function_name: str):
        """
        Create a parametrized fixture that tests all captures.

        Args:
            function_name: Name of the function

        Returns:
            Function that can be used as parametrized pytest fixture

        Example:
            # In conftest.py
            capture_fixture = CaptureFixture()

            @pytest.fixture(params=capture_fixture.create_parametrized_fixture("process_data"))
            def all_process_data_args(request):
                return request.param

            # In test file
            def test_process_data_all(all_process_data_args):
                args, kwargs = all_process_data_args
                result = process_data(*args, **kwargs)
                assert result is not None
        """
        captures = self.loader.load_all(function_name)
        if not captures:
            raise ValueError(f"No captures found for function '{function_name}'")
        return captures