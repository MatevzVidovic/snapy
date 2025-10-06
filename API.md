# Snapy API Reference

## Main Module (`snapy`)

### Direct Imports
```python
from snapy import capture_args, load_capture, load_capture_dict, CaptureConfig
from snapy import FunctionTracer, CallEvent, TracedSnapshot
```

## Capture System (`snapy.capture`)

### Decorators

#### `@capture_args()`
```python
@capture_args(
    path: Optional[str] = None,
    retention: Optional[int] = None,
    overwrite: Optional[bool] = None,
    ignore_args: Optional[List[str]] = None,
    config: Optional[CaptureConfig] = None,
    enabled: Optional[bool] = None
) -> Callable
```

**Parameters:**
- `path` - Custom storage path (overrides config default)
- `retention` - Number of captures to retain (overrides config default)
- `overwrite` - Whether to overwrite existing captures (overrides config default)
- `ignore_args` - Additional argument names to ignore (extends config)
- `config` - Custom CaptureConfig instance (overrides global config)
- `enabled` - Override global enable/disable setting

**Usage:**
- Supports both sync and async functions
- Automatically captures function arguments when called
- Applies argument filtering for sensitive data

### Loading Functions

#### `load_capture()`
```python
load_capture(
    function_name: str,
    index: int = 0,
    path: Optional[str] = None,
    latest: bool = True
) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]
```

**Parameters:**
- `function_name` - Name of the function
- `index` - Index of the capture (0-based, 0 = most recent)
- `path` - Custom path to search for captures
- `latest` - Whether to load the latest capture (default: True)

**Returns:** Tuple of `(args, kwargs)` or `None` if not found

#### `load_capture_dict()`
```python
load_capture_dict(
    function_name: str,
    index: int = 0,
    path: Optional[str] = None,
    latest: bool = True
) -> Optional[OrderedDict[str, Any]]
```

**Parameters:** Same as `load_capture()`

**Returns:** OrderedDict with parameter names as keys or `None` if not found

#### `has_capture()`
```python
has_capture(
    function_name: str,
    path: Optional[str] = None
) -> bool
```

**Parameters:**
- `function_name` - Name of the function
- `path` - Custom path to search for captures

**Returns:** `True` if captures exist for the function

### Configuration

#### `CaptureConfig`
```python
@dataclass
class CaptureConfig:
    enabled: bool = True
    default_path: str = "./snap_capture"
    default_retention: int = 2
    default_overwrite: bool = False
    ignore_modules: List[str] = field(default_factory=list)
    ignore_functions: List[str] = field(default_factory=list)
    ignore_args: List[str] = field(default_factory=lambda: ["password", "token", "secret", "key", "auth"])
    production_mode: bool = False
    minimal_capture: bool = False
    serialization_backend: str = "dill"
    fallback_to_dill: bool = True
```

**Class Methods:**
```python
CaptureConfig.from_env_file(env_file_path: Optional[str] = None) -> CaptureConfig
```

#### `CaptureLoader`
```python
class CaptureLoader:
    def __init__(self, base_path: Optional[str] = None)

    def load_latest(self, function_name: str) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]
    def load_by_index(self, function_name: str, index: int = 0) -> Optional[Tuple[Tuple[Any, ...], Dict[str, Any]]]
    def load_capture_object(self, function_name: str, index: int = 0) -> Optional[CapturedCall]
    def list_captures(self, function_name: Optional[str] = None) -> List[str]
    def has_captures(self, function_name: str) -> bool
```

#### `CaptureStorage`
```python
class CaptureStorage:
    def __init__(self, base_path: str)

    def save_capture(self, capture: CapturedCall) -> str
    def load_capture(self, file_path: str) -> Optional[CapturedCall]
    def load_latest_capture(self, function_name: str) -> Optional[CapturedCall]
    def load_capture_by_index(self, function_name: str, index: int = 0) -> Optional[CapturedCall]
    def list_function_captures(self, function_name: str) -> List[str]
    def cleanup_old_captures(self, function_name: str, retention: int)
```

#### `ArgumentFilter`
```python
class ArgumentFilter:
    def __init__(self, config: CaptureConfig)

    def filter_args(self, args: tuple, kwargs: dict, function_name: str) -> Tuple[tuple, dict]
    def should_ignore_arg(self, arg_name: str) -> bool
    def add_ignore_pattern(self, pattern: str)
```

## Testing System (`snapy.testing`)

### Function Tracing

#### `FunctionTracer`
```python
class FunctionTracer:
    def __init__(self, filter_modules: Optional[List[str]] = None)

    def start_tracing(self) -> None
    def stop_tracing(self) -> None
    def get_events(self) -> List[CallEvent]
    def get_trace(self) -> List[CallEvent]
    def clear_events(self) -> None
    def should_trace_frame(self, frame: FrameType) -> bool
    def extract_args(self, frame: FrameType) -> Dict[str, Any]
```

**Context Manager Usage:**
```python
with tracer:
    # Code to trace
    result = function_to_trace()
```

**Parameters:**
- `filter_modules` - List of module name patterns to trace (None = trace all non-system modules)

#### `CallEvent`
```python
@dataclass
class CallEvent:
    event_type: str  # 'call', 'return', or 'exception'
    function_name: str
    filename: str
    line_number: int
    args: Dict[str, Any] = field(default_factory=dict)
    return_value: Any = None
    depth: int = 0
    timestamp: float = 0.0
```

### Snapshot Integration

#### `TracedSnapshot`
```python
class TracedSnapshot:
    def __init__(self, tracer: Optional[FunctionTracer] = None)

    def capture_trace(self, func: callable, *args, **kwargs) -> Any
    def format_trace_snapshot(self, include_result: bool = True) -> str
    def get_last_trace(self) -> Optional[List[CallEvent]]
    def clear_traces(self) -> None
```

**Parameters:**
- `tracer` - FunctionTracer instance (creates new one if None)

## Environment Variables

### Core Configuration
- `SNAP_CAPTURE_ENABLED` - Global enable/disable (default: "true")
- `SNAP_CAPTURE_DEFAULT_PATH` - Storage location (default: "./snap_capture")
- `SNAP_CAPTURE_DEFAULT_RETENTION` - Number of captures to keep (default: "2")
- `SNAP_CAPTURE_DEFAULT_OVERWRITE` - Overwrite existing captures (default: "false")

### Filtering
- `SNAP_CAPTURE_IGNORE_MODULES` - Comma-separated module patterns to ignore
- `SNAP_CAPTURE_IGNORE_FUNCTIONS` - Comma-separated function patterns to ignore
- `SNAP_CAPTURE_IGNORE_ARGS` - Comma-separated argument names to filter (default: "password,token,secret,key,auth")

### Serialization
- `SNAP_CAPTURE_SERIALIZATION_BACKEND` - Backend to use (default: "dill")
- `SNAP_CAPTURE_FALLBACK_TO_DILL` - Auto-fallback to dill if pickle fails (default: "true")

### Production Settings
- `SNAP_CAPTURE_PRODUCTION_MODE` - Minimal overhead mode (default: "false")
- `SNAP_CAPTURE_MINIMAL` - Essential data only (default: "false")

## Return Types

### `CapturedCall`
```python
@dataclass
class CapturedCall:
    function_name: str
    module_name: str
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    timestamp: float
    call_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)
```