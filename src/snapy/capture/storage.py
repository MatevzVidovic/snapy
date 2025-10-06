"""
Storage management for captured function arguments.
"""

import pickle
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple, Optional, Dict
from dataclasses import dataclass
from collections import OrderedDict
import glob
import os
from .config import get_global_config


@dataclass
class CaptureMetadata:
    """Metadata for a captured function call."""
    function_name: str
    module_name: str
    timestamp: datetime
    args_count: int
    file_path: str


@dataclass
class CapturedCall:
    """A captured function call with arguments and metadata."""
    metadata: CaptureMetadata
    args_dict: OrderedDict[str, Any]

    @property
    def args(self) -> Tuple[Any, ...]:
        """Get positional arguments as tuple for backward compatibility."""
        return tuple(self.args_dict.values())

    @property
    def kwargs(self) -> Dict[str, Any]:
        """Get keyword arguments as dict for backward compatibility (empty since all args are positional)."""
        return {}


class CaptureStorage:
    """
    Manages persistence of captured function arguments.

    Handles file operations, retention policies, and thread-safe storage.
    """

    def __init__(self, base_path: str = "./snap_capture"):
        """
        Initialize storage manager.

        Args:
            base_path: Base directory for storing captures
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._setup_serializer()

    def _setup_serializer(self):
        """Setup the serialization backend based on configuration."""
        config = get_global_config()
        backend = config.get_serialization_backend()

        if backend == "dill":
            dill_module = self._get_dill()
            if dill_module:
                self.serializer = dill_module
                self.serializer_name = "dill"
            else:
                print("Warning: dill not available, falling back to pickle")
                self.serializer = pickle
                self.serializer_name = "pickle"
        elif backend == "pickle":
            self.serializer = pickle
            self.serializer_name = "pickle"
        else:  # auto
            # Try dill first, fallback to pickle
            dill_module = self._get_dill()
            if dill_module:
                self.serializer = dill_module
                self.serializer_name = "dill"
            else:
                self.serializer = pickle
                self.serializer_name = "pickle"

    def _get_dill(self):
        """Get dill module if available."""
        try:
            import dill
            return dill
        except ImportError:
            return None

    def _safe_serialize(self, obj: Any, filepath: Path) -> None:
        """
        Safely serialize object with fallback mechanism.

        Args:
            obj: Object to serialize
            filepath: Path to save the serialized object
        """
        config = get_global_config()

        try:
            # Try with primary serializer
            with open(filepath, 'wb') as f:
                self.serializer.dump(obj, f)
            return
        except Exception as primary_error:
            # If fallback is enabled and we're using pickle, try dill
            if (config.should_fallback_to_dill() and
                self.serializer_name == "pickle"):

                dill_module = self._get_dill()
                if dill_module:
                    try:
                        with open(filepath, 'wb') as f:
                            dill_module.dump(obj, f)
                        print(f"Note: Used dill serialization fallback for {filepath.name}")
                        return
                    except Exception:
                        # If dill also fails, raise original pickle error
                        pass

            # If no fallback worked, raise the original error
            raise primary_error

    def _safe_deserialize(self, filepath: Path) -> Any:
        """
        Safely deserialize object with fallback mechanism.

        Args:
            filepath: Path to the serialized object

        Returns:
            Deserialized object
        """
        config = get_global_config()

        try:
            # Try with primary serializer
            with open(filepath, 'rb') as f:
                return self.serializer.load(f)
        except Exception as primary_error:
            # If fallback is enabled and we're using pickle, try dill
            if (config.should_fallback_to_dill() and
                self.serializer_name == "pickle"):

                dill_module = self._get_dill()
                if dill_module:
                    try:
                        with open(filepath, 'rb') as f:
                            return dill_module.load(f)
                    except Exception:
                        # If dill also fails, raise original pickle error
                        pass

            # If no fallback worked, raise the original error
            raise primary_error

    def save_capture(
        self,
        function_name: str,
        module_name: str,
        args_dict: OrderedDict[str, Any],
        retention: int = 2,
        overwrite: bool = False
    ) -> str:
        """
        Save a function call capture.

        Args:
            function_name: Name of the captured function
            module_name: Module containing the function
            args_dict: Ordered dictionary of argument names to values
            retention: Number of captures to retain for this function
            overwrite: Whether to overwrite existing captures

        Returns:
            Path to the saved capture file
        """
        with self._lock:
            # Check if we should skip saving based on overwrite policy
            if not overwrite and self._has_existing_captures(function_name):
                existing_files = self.list_captures(function_name)
                if existing_files:
                    return existing_files[0].metadata.file_path

            # Generate filename with timestamp
            timestamp = datetime.now()
            filename = self._generate_filename(function_name, timestamp)
            file_path = self.base_path / filename

            # Create metadata
            metadata = CaptureMetadata(
                function_name=function_name,
                module_name=module_name,
                timestamp=timestamp,
                args_count=len(args_dict),
                file_path=str(file_path)
            )

            # Create capture object
            capture = CapturedCall(
                metadata=metadata,
                args_dict=args_dict
            )

            # Save to file atomically
            self._save_to_file(capture, file_path)

            # Clean up old captures based on retention policy
            self._cleanup_old_captures(function_name, retention)

            return str(file_path)

    def load_capture(self, file_path: str) -> Optional[CapturedCall]:
        """
        Load a capture from file.

        Args:
            file_path: Path to the capture file

        Returns:
            CapturedCall object or None if file doesn't exist or is corrupted
        """
        try:
            return self._safe_deserialize(file_path)
        except (FileNotFoundError, EOFError) as e:
            print(f"Warning: Failed to load capture from {file_path}: {e}")
            return None
        except Exception as e:
            print(f"Warning: Failed to deserialize capture from {file_path}: {e}")
            return None

    def load_latest_capture(self, function_name: str) -> Optional[CapturedCall]:
        """
        Load the most recent capture for a function.

        Args:
            function_name: Name of the function

        Returns:
            Most recent CapturedCall or None if no captures exist
        """
        captures = self.list_captures(function_name)
        return captures[0] if captures else None

    def load_capture_by_index(self, function_name: str, index: int = 0) -> Optional[CapturedCall]:
        """
        Load a capture by index (0 = most recent).

        Args:
            function_name: Name of the function
            index: Index of the capture (0-based, 0 = most recent)

        Returns:
            CapturedCall at the specified index or None if not found
        """
        captures = self.list_captures(function_name)
        if 0 <= index < len(captures):
            return captures[index]
        return None

    def list_captures(self, function_name: str) -> List[CapturedCall]:
        """
        List all captures for a function, sorted by timestamp (newest first).

        Args:
            function_name: Name of the function

        Returns:
            List of CapturedCall objects sorted by timestamp (newest first)
        """
        pattern = f"{function_name}_*.pkl"
        file_pattern = str(self.base_path / pattern)
        capture_files = glob.glob(file_pattern)

        captures = []
        for file_path in capture_files:
            capture = self.load_capture(file_path)
            if capture:
                captures.append(capture)

        # Sort by timestamp, newest first
        captures.sort(key=lambda c: c.metadata.timestamp, reverse=True)
        return captures

    def list_all_functions(self) -> List[str]:
        """
        List all functions that have captures.

        Returns:
            List of function names that have stored captures
        """
        pattern = str(self.base_path / "*.pkl")
        capture_files = glob.glob(pattern)

        function_names = set()
        for file_path in capture_files:
            filename = os.path.basename(file_path)
            if filename.endswith('.pkl'):
                # Extract function name from filename (before first underscore)
                function_name = filename.split('_')[0]
                function_names.add(function_name)

        return sorted(list(function_names))

    def delete_captures(self, function_name: str) -> int:
        """
        Delete all captures for a function.

        Args:
            function_name: Name of the function

        Returns:
            Number of files deleted
        """
        with self._lock:
            captures = self.list_captures(function_name)
            deleted_count = 0

            for capture in captures:
                try:
                    os.remove(capture.metadata.file_path)
                    deleted_count += 1
                except OSError:
                    pass

            return deleted_count

    def cleanup_all_captures(self, retention: int = 2) -> int:
        """
        Clean up all captures across all functions based on retention policy.

        Args:
            retention: Number of captures to retain per function

        Returns:
            Total number of files deleted
        """
        with self._lock:
            deleted_count = 0
            for function_name in self.list_all_functions():
                deleted_count += self._cleanup_old_captures(function_name, retention)
            return deleted_count

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dictionary with storage statistics
        """
        functions = self.list_all_functions()
        total_files = 0
        total_size = 0

        function_stats = {}
        for function_name in functions:
            captures = self.list_captures(function_name)
            function_files = len(captures)
            function_size = sum(
                os.path.getsize(capture.metadata.file_path)
                for capture in captures
                if os.path.exists(capture.metadata.file_path)
            )

            function_stats[function_name] = {
                "file_count": function_files,
                "total_size_bytes": function_size,
                "latest_capture": captures[0].metadata.timestamp if captures else None
            }

            total_files += function_files
            total_size += function_size

        return {
            "total_functions": len(functions),
            "total_files": total_files,
            "total_size_bytes": total_size,
            "storage_path": str(self.base_path),
            "function_stats": function_stats
        }

    def _has_existing_captures(self, function_name: str) -> bool:
        """Check if any captures exist for a function."""
        return bool(self.list_captures(function_name))

    def _generate_filename(self, function_name: str, timestamp: datetime) -> str:
        """Generate a filename for a capture."""
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S_%f")[:-3]  # Include milliseconds
        return f"{function_name}_{timestamp_str}.pkl"

    def _save_to_file(self, capture: CapturedCall, file_path: Path) -> None:
        """Save capture to file atomically."""
        # Use temporary file for atomic write
        # Use safe serialization with fallback mechanism
        with tempfile.NamedTemporaryFile(
            mode='wb',
            dir=file_path.parent,
            delete=False
        ) as temp_file:
            # Close the temp file so we can use our safe serialization method
            temp_file_path = Path(temp_file.name)

        try:
            self._safe_serialize(capture, temp_file_path)
            # Atomic rename
            os.rename(temp_file_path, file_path)
        except Exception:
            # Clean up temp file if serialization failed
            if temp_file_path.exists():
                temp_file_path.unlink()
            raise

    def _cleanup_old_captures(self, function_name: str, retention: int) -> int:
        """Clean up old captures based on retention policy."""
        captures = self.list_captures(function_name)

        if len(captures) <= retention:
            return 0

        # Remove oldest captures beyond retention limit
        old_captures = captures[retention:]
        deleted_count = 0

        for capture in old_captures:
            try:
                os.remove(capture.metadata.file_path)
                deleted_count += 1
            except OSError:
                pass

        return deleted_count