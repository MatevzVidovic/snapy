"""
Production optimizations and performance monitoring for snap capture.
"""

import time
import threading
import os
import sys
from contextlib import contextmanager
from typing import Any, Dict, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class PerformanceMetrics:
    """Performance metrics for capture operations."""
    total_captures: int = 0
    total_capture_time: float = 0.0
    total_serialization_time: float = 0.0
    total_file_write_time: float = 0.0
    average_capture_time: float = 0.0
    peak_capture_time: float = 0.0
    failed_captures: int = 0
    total_bytes_written: int = 0
    captures_per_function: Dict[str, int] = field(default_factory=dict)


class PerformanceMonitor:
    """
    Monitors and optimizes capture performance in production environments.
    """

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = PerformanceMetrics()
        self._lock = threading.Lock()
        self._start_time = time.time()

    @contextmanager
    def measure_capture(self, function_name: str):
        """
        Context manager to measure capture performance.

        Args:
            function_name: Name of the function being captured

        Yields:
            Performance measurement context
        """
        start_time = time.perf_counter()
        try:
            yield
            # Success case
            end_time = time.perf_counter()
            capture_time = end_time - start_time

            with self._lock:
                self.metrics.total_captures += 1
                self.metrics.total_capture_time += capture_time
                self.metrics.average_capture_time = (
                    self.metrics.total_capture_time / self.metrics.total_captures
                )
                self.metrics.peak_capture_time = max(
                    self.metrics.peak_capture_time, capture_time
                )
                self.metrics.captures_per_function[function_name] = (
                    self.metrics.captures_per_function.get(function_name, 0) + 1
                )

        except Exception:
            # Failure case
            with self._lock:
                self.metrics.failed_captures += 1
            raise

    def add_serialization_time(self, time_seconds: float):
        """Record serialization time."""
        with self._lock:
            self.metrics.total_serialization_time += time_seconds

    def add_file_write_time(self, time_seconds: float, bytes_written: int):
        """Record file write time and size."""
        with self._lock:
            self.metrics.total_file_write_time += time_seconds
            self.metrics.total_bytes_written += bytes_written

    def get_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics."""
        with self._lock:
            return PerformanceMetrics(
                total_captures=self.metrics.total_captures,
                total_capture_time=self.metrics.total_capture_time,
                total_serialization_time=self.metrics.total_serialization_time,
                total_file_write_time=self.metrics.total_file_write_time,
                average_capture_time=self.metrics.average_capture_time,
                peak_capture_time=self.metrics.peak_capture_time,
                failed_captures=self.metrics.failed_captures,
                total_bytes_written=self.metrics.total_bytes_written,
                captures_per_function=self.metrics.captures_per_function.copy()
            )

    def should_throttle_capture(self, function_name: str) -> bool:
        """
        Determine if captures should be throttled for performance.

        Args:
            function_name: Name of the function

        Returns:
            True if captures should be throttled
        """
        metrics = self.get_metrics()

        # Throttle if average capture time is too high
        if metrics.average_capture_time > 0.1:  # 100ms threshold
            return True

        # Throttle if this function is captured too frequently
        function_captures = metrics.captures_per_function.get(function_name, 0)
        if function_captures > 100:  # Max 100 captures per function per session
            return True

        # Throttle if too many recent failures
        if metrics.failed_captures > 10:
            return True

        return False

    def reset_metrics(self):
        """Reset performance metrics."""
        with self._lock:
            self.metrics = PerformanceMetrics()
            self._start_time = time.time()

    def get_performance_report(self) -> str:
        """
        Generate a human-readable performance report.

        Returns:
            Performance report string
        """
        metrics = self.get_metrics()
        uptime = time.time() - self._start_time

        report = f"""
Snap Capture Performance Report
==============================
Uptime: {uptime:.2f} seconds
Total Captures: {metrics.total_captures}
Failed Captures: {metrics.failed_captures}
Success Rate: {((metrics.total_captures - metrics.failed_captures) / max(metrics.total_captures, 1)) * 100:.1f}%

Timing Metrics:
  Average Capture Time: {metrics.average_capture_time * 1000:.2f}ms
  Peak Capture Time: {metrics.peak_capture_time * 1000:.2f}ms
  Total Capture Time: {metrics.total_capture_time:.2f}s
  Total Serialization Time: {metrics.total_serialization_time:.2f}s
  Total File Write Time: {metrics.total_file_write_time:.2f}s

Data Metrics:
  Total Bytes Written: {metrics.total_bytes_written:,} bytes
  Average Bytes per Capture: {metrics.total_bytes_written / max(metrics.total_captures, 1):.0f} bytes

Top Functions by Capture Count:
"""
        # Sort functions by capture count
        sorted_functions = sorted(
            metrics.captures_per_function.items(),
            key=lambda x: x[1],
            reverse=True
        )

        for func_name, count in sorted_functions[:10]:  # Top 10
            report += f"  {func_name}: {count} captures\n"

        return report


class ProductionOptimizer:
    """
    Applies optimizations for production environments.
    """

    def __init__(self, performance_monitor: PerformanceMonitor):
        """
        Initialize production optimizer.

        Args:
            performance_monitor: PerformanceMonitor instance
        """
        self.monitor = performance_monitor
        self._optimization_level = self._detect_optimization_level()

    def _detect_optimization_level(self) -> str:
        """
        Detect appropriate optimization level based on environment.

        Returns:
            Optimization level: 'development', 'staging', or 'production'
        """
        # Check environment variables
        env = os.getenv('ENVIRONMENT', '').lower()
        if env in ['prod', 'production']:
            return 'production'
        elif env in ['staging', 'test']:
            return 'staging'

        # Check if running in typical production indicators
        if any([
            os.getenv('KUBERNETES_SERVICE_HOST'),  # Kubernetes
            os.getenv('AWS_LAMBDA_FUNCTION_NAME'),  # Lambda
            os.getenv('HEROKU_APP_NAME'),  # Heroku
            os.getenv('GOOGLE_CLOUD_PROJECT'),  # GCP
        ]):
            return 'production'

        return 'development'

    def should_capture(self, function_name: str, module_name: str) -> bool:
        """
        Determine if a function should be captured based on optimization level.

        Args:
            function_name: Name of the function
            module_name: Name of the module

        Returns:
            True if capture should proceed
        """
        if self._optimization_level == 'production':
            # Very conservative in production
            if self.monitor.should_throttle_capture(function_name):
                return False

            # Skip capturing for system modules
            if any(module_name.startswith(prefix) for prefix in [
                'sys', 'os', 'threading', 'logging', 'json', 'pickle'
            ]):
                return False

        elif self._optimization_level == 'staging':
            # Moderate throttling in staging
            if self.monitor.should_throttle_capture(function_name):
                return False

        # Always capture in development
        return True

    def optimize_arguments(self, args: tuple, kwargs: dict) -> tuple:
        """
        Optimize arguments for storage based on environment.

        Args:
            args: Original arguments
            kwargs: Original keyword arguments

        Returns:
            Tuple of (optimized_args, optimized_kwargs)
        """
        if self._optimization_level == 'production':
            # Aggressive optimization for production
            return self._minimize_arguments(args, kwargs)
        elif self._optimization_level == 'staging':
            # Moderate optimization for staging
            return self._reduce_large_arguments(args, kwargs)
        else:
            # No optimization for development
            return args, kwargs

    def _minimize_arguments(self, args: tuple, kwargs: dict) -> tuple:
        """Minimize arguments for production use."""
        # Convert to type information only
        minimal_args = tuple(
            f"<{type(arg).__name__}:{self._get_size_description(arg)}>"
            for arg in args
        )

        minimal_kwargs = {
            key: f"<{type(value).__name__}:{self._get_size_description(value)}>"
            for key, value in kwargs.items()
        }

        return minimal_args, minimal_kwargs

    def _reduce_large_arguments(self, args: tuple, kwargs: dict) -> tuple:
        """Reduce size of large arguments."""
        MAX_SIZE = 1024 * 10  # 10KB limit

        reduced_args = []
        for arg in args:
            if self._estimate_size(arg) > MAX_SIZE:
                reduced_args.append(f"<LARGE_{type(arg).__name__}>")
            else:
                reduced_args.append(arg)

        reduced_kwargs = {}
        for key, value in kwargs.items():
            if self._estimate_size(value) > MAX_SIZE:
                reduced_kwargs[key] = f"<LARGE_{type(value).__name__}>"
            else:
                reduced_kwargs[key] = value

        return tuple(reduced_args), reduced_kwargs

    def _estimate_size(self, obj: Any) -> int:
        """Estimate object size in bytes."""
        try:
            return sys.getsizeof(obj)
        except (TypeError, AttributeError):
            return 1000  # Conservative estimate

    def _get_size_description(self, obj: Any) -> str:
        """Get human-readable size description."""
        size = self._estimate_size(obj)
        if size < 1024:
            return f"{size}B"
        elif size < 1024 * 1024:
            return f"{size // 1024}KB"
        else:
            return f"{size // (1024 * 1024)}MB"

    def get_optimization_level(self) -> str:
        """Get current optimization level."""
        return self._optimization_level


# Global instances
_performance_monitor = PerformanceMonitor()
_production_optimizer = ProductionOptimizer(_performance_monitor)


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _performance_monitor


def get_production_optimizer() -> ProductionOptimizer:
    """Get global production optimizer instance."""
    return _production_optimizer


def configure_for_production():
    """
    Configure snap capture for optimal production performance.

    This function should be called at application startup in production.
    """
    # Set environment variable to ensure production mode
    os.environ['SNAP_CAPTURE_PRODUCTION_MODE'] = 'true'
    os.environ['SNAP_CAPTURE_MINIMAL'] = 'true'

    # Reset metrics for clean start
    _performance_monitor.reset_metrics()


def print_performance_report():
    """Print current performance report to stdout."""
    print(_performance_monitor.get_performance_report())


@contextmanager
def performance_context():
    """
    Context manager for performance monitoring.

    Example:
        with performance_context():
            # Run code with performance monitoring
            some_captured_function()

        print_performance_report()
    """
    start_metrics = _performance_monitor.get_metrics()
    try:
        yield _performance_monitor
    finally:
        end_metrics = _performance_monitor.get_metrics()
        captures_in_context = end_metrics.total_captures - start_metrics.total_captures
        time_in_context = end_metrics.total_capture_time - start_metrics.total_capture_time

        if captures_in_context > 0:
            print(f"Performance Context: {captures_in_context} captures in {time_in_context:.2f}s "
                  f"(avg: {time_in_context / captures_in_context * 1000:.2f}ms per capture)")


class CaptureProfiler:
    """
    Profiler for detailed analysis of capture performance.
    """

    def __init__(self):
        """Initialize capture profiler."""
        self.profiles: List[Dict[str, Any]] = []
        self._lock = threading.Lock()

    def profile_capture(
        self,
        function_name: str,
        capture_time: float,
        serialization_time: float,
        file_write_time: float,
        bytes_written: int,
        args_count: int,
        kwargs_count: int
    ):
        """
        Record detailed profile information for a capture.

        Args:
            function_name: Name of the captured function
            capture_time: Total capture time
            serialization_time: Time spent serializing
            file_write_time: Time spent writing to file
            bytes_written: Number of bytes written
            args_count: Number of positional arguments
            kwargs_count: Number of keyword arguments
        """
        profile = {
            'timestamp': datetime.now().isoformat(),
            'function_name': function_name,
            'capture_time': capture_time,
            'serialization_time': serialization_time,
            'file_write_time': file_write_time,
            'bytes_written': bytes_written,
            'args_count': args_count,
            'kwargs_count': kwargs_count,
            'overhead_ratio': (capture_time - serialization_time - file_write_time) / capture_time
        }

        with self._lock:
            self.profiles.append(profile)

            # Keep only last 1000 profiles to prevent memory growth
            if len(self.profiles) > 1000:
                self.profiles = self.profiles[-1000:]

    def get_slowest_captures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the slowest captures.

        Args:
            limit: Maximum number of results

        Returns:
            List of profile dictionaries sorted by capture time
        """
        with self._lock:
            return sorted(
                self.profiles,
                key=lambda p: p['capture_time'],
                reverse=True
            )[:limit]

    def get_largest_captures(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the largest captures by bytes written.

        Args:
            limit: Maximum number of results

        Returns:
            List of profile dictionaries sorted by bytes written
        """
        with self._lock:
            return sorted(
                self.profiles,
                key=lambda p: p['bytes_written'],
                reverse=True
            )[:limit]

    def clear_profiles(self):
        """Clear all profile data."""
        with self._lock:
            self.profiles.clear()


# Global profiler instance
_capture_profiler = CaptureProfiler()


def get_capture_profiler() -> CaptureProfiler:
    """Get global capture profiler instance."""
    return _capture_profiler