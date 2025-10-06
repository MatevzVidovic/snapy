# snapy_testing API Reference

## Core Classes and Functions

### FunctionTracer Class

```python
class FunctionTracer:
    def __init__(
        self,
        filter_modules: Optional[List[str]] = None,
        max_depth: Optional[int] = None,
        capture_args: bool = True,
        capture_returns: bool = True,
        capture_exceptions: bool = True
    )
```

**Description**: Core tracing engine using sys.settrace for function call interception.

**Parameters**:
- `filter_modules`: List of module patterns to include/exclude from tracing
- `max_depth`: Maximum call stack depth to trace (None = unlimited)
- `capture_args`: Whether to capture function arguments
- `capture_returns`: Whether to capture return values
- `capture_exceptions`: Whether to capture exception information

**Attributes**:
```python
events: List[CallEvent]              # Captured call events
call_stack: List[CallEvent]          # Current call stack
is_tracing: bool                     # Tracing state
thread_local: threading.local       # Thread-specific data
original_trace: Optional[Callable]   # Original trace function
```

**Methods**:
```python
def start_tracing(self) -> None
    """Begin function call tracing"""

def stop_tracing(self) -> None
    """End function call tracing"""

def get_events(self) -> List[CallEvent]
    """Get all captured call events"""

def get_call_graph(self) -> Dict[str, Any]
    """Build call graph from traced events"""

def get_metrics(self) -> Dict[str, Any]
    """Get performance metrics from trace"""

def clear_events(self) -> None
    """Clear all captured events"""

def format_trace(self, format_type: str = "tree") -> str
    """Format trace events for display"""

def filter_events(
    self,
    function_pattern: str = None,
    module_pattern: str = None,
    min_duration: float = None
) -> List[CallEvent]
    """Filter events by criteria"""
```

**Context Manager Usage**:
```python
with FunctionTracer() as tracer:
    result = function_to_trace()
    events = tracer.get_events()
```

### CallEvent Class

```python
@dataclass
class CallEvent:
    event_type: str                    # 'call', 'return', 'exception'
    function_name: str                 # Function name
    filename: str                      # Source file path
    line_number: int                   # Line number in source
    args: Dict[str, Any]               # Function arguments
    return_value: Any                  # Return value (for 'return' events)
    exception_info: Optional[Tuple]    # Exception details (for 'exception' events)
    depth: int                         # Call stack depth
    timestamp: float                   # Event timestamp
    duration: Optional[float]          # Execution duration (for 'return' events)
    thread_id: str                     # Thread identifier
    memory_usage: Optional[int]        # Memory usage at event
    module_name: str                   # Module containing function
```

**Methods**:
```python
def to_dict(self) -> Dict[str, Any]
    """Convert event to dictionary representation"""

def from_dict(cls, data: Dict[str, Any]) -> 'CallEvent'
    """Create event from dictionary"""

def is_call_event(self) -> bool
    """Check if this is a function call event"""

def is_return_event(self) -> bool
    """Check if this is a function return event"""

def is_exception_event(self) -> bool
    """Check if this is an exception event"""

def get_full_function_name(self) -> str
    """Get fully qualified function name (module.function)"""
```

### TracedSnapshot Class

```python
class TracedSnapshot:
    def __init__(
        self,
        tracer: Optional[FunctionTracer] = None,
        detail_level: str = "standard",
        include_args: bool = True,
        include_returns: bool = True,
        include_timing: bool = True
    )
```

**Description**: Syrupy integration for traced execution snapshots.

**Parameters**:
- `tracer`: Custom FunctionTracer instance (creates default if None)
- `detail_level`: Level of detail in snapshots ("minimal", "standard", "verbose")
- `include_args`: Include function arguments in snapshots
- `include_returns`: Include return values in snapshots
- `include_timing`: Include timing information in snapshots

**Methods**:
```python
def capture_trace(
    self,
    func: Callable,
    *args,
    **kwargs
) -> Any
    """Execute function with tracing and return result"""

def format_trace(self, format_type: str = "structured") -> Dict[str, Any]
    """Format trace for snapshot comparison"""

def get_execution_summary(self) -> Dict[str, Any]
    """Get high-level execution summary"""

def get_performance_metrics(self) -> Dict[str, Any]
    """Get performance metrics from trace"""

def build_call_tree(self) -> Dict[str, Any]
    """Build hierarchical call tree"""
```

**Context Manager Usage**:
```python
traced = TracedSnapshot()
with traced:
    result = complex_function()

snapshot_data = traced.format_trace()
```

## Advanced Features

### Module Filtering

```python
class ModuleFilter:
    def __init__(
        self,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
        use_regex: bool = False
    )
```

**Description**: Configurable module filtering for focused tracing.

**Pattern Syntax**:
- Wildcards: `myapp.*` (includes all myapp submodules)
- Exclusion: `!numpy.*` (excludes numpy modules)
- Regex: Full regex patterns when `use_regex=True`

**Methods**:
```python
def should_trace_module(self, module_name: str) -> bool
    """Determine if module should be traced"""

def add_include_pattern(self, pattern: str) -> None
    """Add pattern to include list"""

def add_exclude_pattern(self, pattern: str) -> None
    """Add pattern to exclude list"""
```

### Performance Tracking

```python
class PerformanceMetrics:
    def __init__(self, events: List[CallEvent])
```

**Description**: Analyzes trace events for performance insights.

**Methods**:
```python
def get_total_execution_time(self) -> float
    """Total time for all traced function calls"""

def get_function_call_counts(self) -> Dict[str, int]
    """Count of calls per function"""

def get_slowest_functions(self, limit: int = 10) -> List[Dict[str, Any]]
    """Functions with highest execution time"""

def get_most_called_functions(self, limit: int = 10) -> List[Dict[str, Any]]
    """Functions called most frequently"""

def get_call_depth_stats(self) -> Dict[str, Any]
    """Statistics about call stack depth"""

def identify_hotspots(self, threshold: float = 0.1) -> List[Dict[str, Any]]
    """Identify performance hotspots"""
```

### Call Graph Analysis

```python
class CallGraphBuilder:
    def __init__(self, events: List[CallEvent])
```

**Description**: Builds call graphs and dependency analysis from trace events.

**Methods**:
```python
def build_graph(self) -> Dict[str, Any]
    """Build complete call graph"""

def get_function_dependencies(self, function_name: str) -> List[str]
    """Get functions called by specified function"""

def get_function_callers(self, function_name: str) -> List[str]
    """Get functions that call specified function"""

def find_cycles(self) -> List[List[str]]
    """Detect recursive call cycles"""

def get_critical_path(self) -> List[str]
    """Find longest execution path"""

def export_graphviz(self) -> str
    """Export graph in Graphviz DOT format"""
```

## Testing Integration

### pytest Integration

```python
@pytest.fixture
def function_tracer():
    """Pytest fixture providing FunctionTracer instance"""
    tracer = FunctionTracer(filter_modules=["myapp.*"])
    yield tracer
    tracer.cleanup()

@pytest.fixture
def traced_snapshot():
    """Pytest fixture providing TracedSnapshot instance"""
    return TracedSnapshot(detail_level="standard")
```

### Test Helper Functions

```python
def create_traced_test(
    test_function: Callable,
    filter_modules: List[str] = None
) -> Callable
    """Decorator to add tracing to test functions"""

def assert_function_called(
    events: List[CallEvent],
    function_name: str,
    min_times: int = 1
) -> None
    """Assert that function was called minimum number of times"""

def assert_call_order(
    events: List[CallEvent],
    expected_order: List[str]
) -> None
    """Assert that functions were called in expected order"""

def assert_no_exceptions(events: List[CallEvent]) -> None
    """Assert that no exceptions occurred during tracing"""
```

## Utility Functions

### Event Analysis

```python
def filter_events_by_function(
    events: List[CallEvent],
    function_pattern: str
) -> List[CallEvent]
    """Filter events by function name pattern"""

def filter_events_by_module(
    events: List[CallEvent],
    module_pattern: str
) -> List[CallEvent]
    """Filter events by module name pattern"""

def filter_events_by_duration(
    events: List[CallEvent],
    min_duration: float = None,
    max_duration: float = None
) -> List[CallEvent]
    """Filter events by execution duration"""

def group_events_by_function(
    events: List[CallEvent]
) -> Dict[str, List[CallEvent]]
    """Group events by function name"""
```

### Trace Formatting

```python
def format_trace_tree(
    events: List[CallEvent],
    include_args: bool = False,
    include_timing: bool = True,
    max_depth: int = None
) -> str
    """Format events as hierarchical tree"""

def format_trace_flat(
    events: List[CallEvent],
    include_timing: bool = True
) -> str
    """Format events as flat list"""

def format_trace_json(
    events: List[CallEvent],
    pretty: bool = True
) -> str
    """Format events as JSON"""

def export_trace_csv(
    events: List[CallEvent],
    filename: str
) -> None
    """Export events to CSV file"""
```

## Exception Classes

```python
class TracingError(Exception):
    """Base exception for tracing-related errors"""

class TracingNotActiveError(TracingError):
    """Raised when operation requires active tracing"""

class FilterError(TracingError):
    """Raised when module filter configuration is invalid"""

class TraceFormatError(TracingError):
    """Raised when trace formatting fails"""

class CallGraphError(TracingError):
    """Raised when call graph analysis fails"""
```

## Configuration Options

### Tracer Configuration

```python
@dataclass
class TracerConfig:
    max_events: int = 10000               # Maximum events to store
    enable_line_tracing: bool = False     # Trace line-by-line execution
    capture_locals: bool = False          # Capture local variables
    capture_globals: bool = False         # Capture global variables
    memory_tracking: bool = False         # Track memory usage
    thread_safety: bool = True            # Enable thread-safe operation
    compression: bool = False             # Compress stored events
    auto_cleanup: bool = True             # Automatic cleanup of old events
```

### Snapshot Configuration

```python
@dataclass
class SnapshotConfig:
    detail_level: str = "standard"        # "minimal", "standard", "verbose"
    max_call_depth: int = 50              # Maximum call depth to capture
    include_system_calls: bool = False    # Include system/stdlib calls
    format_style: str = "structured"      # "tree", "flat", "structured"
    timestamp_precision: int = 6          # Decimal places for timestamps
    sort_by: str = "chronological"        # "chronological", "alphabetical"
```

## Type Annotations

```python
from typing import (
    Any, Dict, List, Optional, Tuple, Callable, Union,
    Iterator, ContextManager, Protocol
)
from types import FrameType, TracebackType
from dataclasses import dataclass
from pathlib import Path

# Type aliases
TraceFunction = Callable[[FrameType, str, Any], Optional[Callable]]
EventFilter = Callable[[CallEvent], bool]
FormatFunction = Callable[[List[CallEvent]], str]
MetricsDict = Dict[str, Union[int, float, str, List[Any]]]
```

This comprehensive API reference provides complete coverage of the snapy_testing module's public interface and advanced functionality.