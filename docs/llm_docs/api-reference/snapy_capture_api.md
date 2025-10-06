# snapy_capture API Reference

## Core Functions and Classes

### @capture_args() Decorator

```python
def capture_args(
    path: Optional[str] = None,
    retention: Optional[int] = None,
    overwrite: Optional[bool] = None,
    ignore_args: Optional[List[str]] = None,
    config: Optional[CaptureConfig] = None,
    enabled: Optional[bool] = None
) -> Callable[[F], F]
```

**Description**: Primary decorator for capturing function arguments during execution.

**Parameters**:
- `path`: Custom storage directory (overrides global config)
- `retention`: Number of captures to retain per function (default: 2)
- `overwrite`: Whether to overwrite existing captures (default: False)
- `ignore_args`: Additional argument names to filter (extends global config)
- `config`: Custom CaptureConfig instance (overrides global)
- `enabled`: Override global enable/disable setting

**Returns**: Decorated function with argument capture capability

**Usage Examples**:
```python
# Basic usage
@capture_args()
def simple_function(a, b):
    return a + b

# Advanced configuration
@capture_args(
    path="./custom_captures",
    retention=5,
    ignore_args=["password", "api_key"],
    overwrite=True
)
def secure_function(user_id, password, data):
    return authenticate_and_process(user_id, password, data)
```

### CaptureConfig Class

```python
class CaptureConfig:
    def __init__(
        self,
        enabled: bool = True,
        default_path: str = "./snap_capture",
        default_retention: int = 2,
        default_overwrite: bool = False,
        ignore_modules: List[str] = None,
        ignore_functions: List[str] = None,
        ignore_args: List[str] = None,
        production_mode: bool = False,
        minimal_capture: bool = False
    )
```

**Description**: Configuration class for global capture settings.

**Attributes**:
- `enabled`: Global capture enable/disable
- `default_path`: Default storage directory
- `default_retention`: Default retention policy
- `default_overwrite`: Default overwrite behavior
- `ignore_modules`: Module patterns to exclude from capture
- `ignore_functions`: Function patterns to exclude
- `ignore_args`: Argument patterns to filter for security
- `production_mode`: Enable production optimizations
- `minimal_capture`: Capture essential data only

**Methods**:
```python
def from_environment() -> CaptureConfig
    """Create configuration from environment variables"""

def update_from_dict(self, config_dict: Dict[str, Any]) -> None
    """Update configuration from dictionary"""

def to_dict(self) -> Dict[str, Any]
    """Export configuration as dictionary"""
```

### CaptureStorage Class

```python
class CaptureStorage:
    def __init__(
        self,
        base_path: str,
        retention: int = 2,
        compression: bool = False
    )
```

**Description**: Handles persistence and retrieval of captured arguments.

**Methods**:
```python
def store_capture(
    self,
    function_name: str,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    metadata: Dict[str, Any] = None
) -> str
    """Store function arguments to disk"""

def load_capture(
    self,
    function_name: str,
    index: int = 0
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]
    """Load captured arguments from disk"""

def list_captures(self, function_name: str) -> List[Dict[str, Any]]
    """List all available captures for function"""

def cleanup_expired(self, function_name: str = None) -> int
    """Remove old captures based on retention policy"""

def get_storage_stats(self) -> Dict[str, Any]
    """Get storage statistics and usage information"""
```

### ArgumentFilter Class

```python
class ArgumentFilter:
    def __init__(
        self,
        ignore_patterns: List[str] = None,
        max_size: int = None,
        custom_filters: List[Callable] = None
    )
```

**Description**: Filters arguments for security and performance.

**Methods**:
```python
def should_capture_arg(
    self,
    arg_name: str,
    arg_value: Any
) -> bool
    """Determine if argument should be captured"""

def filter_args(
    self,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
    arg_names: List[str]
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]
    """Apply filtering to function arguments"""

def add_pattern(self, pattern: str) -> None
    """Add new filtering pattern"""

def remove_pattern(self, pattern: str) -> None
    """Remove existing filtering pattern"""
```

## Loading Functions

### load_capture()

```python
def load_capture(
    function_name: str,
    index: int = 0,
    storage_path: str = None
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]
```

**Description**: Load captured arguments for replay in tests.

**Parameters**:
- `function_name`: Name of function to load captures for
- `index`: Capture index (0 = most recent, 1 = second most recent, etc.)
- `storage_path`: Custom storage directory (overrides config)

**Returns**: Tuple of (args, kwargs) for function replay

**Raises**:
- `CaptureNotFoundError`: When no captures exist for function
- `CaptureLoadError`: When capture file is corrupted or unreadable

### load_capture_dict()

```python
def load_capture_dict(
    function_name: str,
    index: int = 0,
    storage_path: str = None
) -> Dict[str, Any]
```

**Description**: Load capture as dictionary with metadata.

**Returns**: Dictionary containing:
```python
{
    "args": tuple,
    "kwargs": dict,
    "metadata": {
        "timestamp": str,
        "function_name": str,
        "python_version": str,
        "thread_id": str
    }
}
```

### CaptureLoader Class

```python
class CaptureLoader:
    def __init__(self, storage_path: str = None)
```

**Description**: Advanced capture loading with filtering and selection.

**Methods**:
```python
def load_by_index(
    self,
    function_name: str,
    index: int
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]
    """Load specific capture by index"""

def load_by_timestamp(
    self,
    function_name: str,
    timestamp: datetime
) -> Tuple[Tuple[Any, ...], Dict[str, Any]]
    """Load capture closest to timestamp"""

def load_all(
    self,
    function_name: str
) -> List[Tuple[Tuple[Any, ...], Dict[str, Any]]]
    """Load all available captures for function"""

def search_captures(
    self,
    function_pattern: str = "*",
    metadata_filter: Dict[str, Any] = None
) -> List[Dict[str, Any]]
    """Search captures by function pattern and metadata"""
```

## Utility Functions

### Configuration Management

```python
def get_global_config() -> CaptureConfig
    """Get current global configuration"""

def set_global_config(config: CaptureConfig) -> None
    """Set global configuration"""

def reset_global_config() -> None
    """Reset to default configuration"""
```

### Testing Utilities

```python
def has_capture(function_name: str, storage_path: str = None) -> bool
    """Check if captures exist for function"""

def clear_captures(function_name: str = None, storage_path: str = None) -> int
    """Clear captures for function or all functions"""

def capture_count(function_name: str, storage_path: str = None) -> int
    """Get number of captures for function"""
```

### Context Managers

```python
class CaptureContext:
    def __init__(
        self,
        enabled: bool = None,
        path: str = None,
        config: CaptureConfig = None
    )
```

**Description**: Temporarily override capture configuration.

**Usage**:
```python
# Disable capture in specific context
with CaptureContext(enabled=False):
    sensitive_operation()

# Use different storage path
with CaptureContext(path="./debug_captures"):
    debug_function()
```

## Exception Classes

```python
class CaptureError(Exception):
    """Base exception for capture-related errors"""

class CaptureNotFoundError(CaptureError):
    """Raised when requested capture doesn't exist"""

class CaptureLoadError(CaptureError):
    """Raised when capture file cannot be loaded"""

class CaptureStorageError(CaptureError):
    """Raised when storage operation fails"""

class ConfigurationError(CaptureError):
    """Raised when configuration is invalid"""
```

## Environment Variables

```python
# Global Configuration
SNAP_CAPTURE_ENABLED = "true|false"                    # Enable/disable all capture
SNAP_CAPTURE_DEFAULT_PATH = "./snap_capture"           # Default storage path
SNAP_CAPTURE_DEFAULT_RETENTION = "2"                   # Number of captures to keep
SNAP_CAPTURE_DEFAULT_OVERWRITE = "false"               # Overwrite existing captures

# Security Filtering
SNAP_CAPTURE_IGNORE_MODULES = "module1,module2"        # Modules to ignore
SNAP_CAPTURE_IGNORE_FUNCTIONS = "func1,func2"          # Functions to ignore
SNAP_CAPTURE_IGNORE_ARGS = "password,token,secret"     # Arguments to filter

# Performance Settings
SNAP_CAPTURE_PRODUCTION_MODE = "false"                 # Production optimizations
SNAP_CAPTURE_MINIMAL = "false"                         # Minimal capture mode
SNAP_CAPTURE_MAX_SIZE = "1048576"                      # Max capture size (bytes)
SNAP_CAPTURE_COMPRESSION = "false"                     # Enable compression
```

## Type Annotations

```python
from typing import Any, Dict, List, Optional, Tuple, Callable, Union
from types import FunctionType
from pathlib import Path

# Type aliases for common patterns
CaptureData = Tuple[Tuple[Any, ...], Dict[str, Any]]
CaptureMetadata = Dict[str, Any]
FilterFunction = Callable[[str, Any], bool]
SerializerFunction = Callable[[Any], bytes]
```

This comprehensive API reference provides complete coverage of the snapy_capture module's public interface and functionality.