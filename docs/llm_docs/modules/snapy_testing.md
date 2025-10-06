# snapy_testing Module Documentation

## Overview

The snapy_testing module provides comprehensive function call tracing and execution flow capture using Python's sys.settrace mechanism. It integrates with syrupy snapshot testing to enable validation of complete execution contexts, not just function outputs.

## Core Components

### 1. tracer.py - Function Call Tracing Engine

**Primary Class**: `FunctionTracer`
- Implements sys.settrace-based function call interception
- Captures complete execution flow including nested calls
- Maintains call stack with depth tracking
- Provides thread-safe operation for concurrent testing

**Key Features**:
- Real-time function call event generation
- Configurable module filtering for focused tracing
- Argument and return value capture
- Performance metrics collection (timing, call counts)
- Memory-efficient event storage

**Core Implementation**:
```python
class FunctionTracer:
    def __init__(self, filter_modules=None):
        self.filter_modules = filter_modules or []
        self.events = []
        self.call_stack = []
        self.thread_local = threading.local()

    def trace_function(self, frame, event, arg):
        if event == 'call':
            self._handle_function_call(frame, arg)
        elif event == 'return':
            self._handle_function_return(frame, arg)
        return self.trace_function
```

**Event Types Captured**:
- Function entry with arguments
- Function exit with return values
- Exception handling and propagation
- Line-by-line execution (optional)
- Performance timing data

### 2. snapshot.py - Syrupy Integration Layer

**Primary Class**: `TracedSnapshot`
- Extends syrupy functionality with execution tracing
- Provides custom serialization for call events
- Integrates traced execution with snapshot assertions
- Handles complex object graph serialization

**Key Features**:
- Automatic trace formatting for readable snapshots
- Configurable detail levels (minimal, standard, verbose)
- Integration with syrupy's filtering system
- Support for custom trace serializers

**Usage Pattern**:
```python
def test_complex_business_logic(snapshot):
    traced = TracedSnapshot()

    with traced:
        result = complex_business_function(test_data)

    # Capture both result and execution trace
    combined_snapshot = {
        "result": result,
        "execution_trace": traced.format_trace(),
        "performance_metrics": traced.get_metrics()
    }

    assert combined_snapshot == snapshot
```

### 3. CallEvent Data Structure

**Primary Class**: `CallEvent`
- Represents individual function call occurrences
- Contains comprehensive execution context
- Supports serialization for snapshot storage
- Enables call graph reconstruction

**CallEvent Structure**:
```python
@dataclass
class CallEvent:
    event_type: str          # 'call' or 'return'
    function_name: str       # Function identifier
    filename: str            # Source file path
    line_number: int         # Execution line
    args: Dict[str, Any]     # Function arguments
    return_value: Any        # Function output
    depth: int               # Call stack depth
    timestamp: float         # Execution timing
    thread_id: str           # Thread identifier
    memory_usage: int        # Memory consumption
```

## Advanced Tracing Features

### Module Filtering

**Focused Tracing**:
```python
# Trace only application modules, exclude standard library
tracer = FunctionTracer(filter_modules=[
    "myapp.*",           # Application code
    "business_logic.*",  # Business modules
    "!numpy.*",          # Exclude numpy
    "!pandas.*"          # Exclude pandas
])
```

**Pattern Matching**:
- Positive patterns: Include matching modules
- Negative patterns (prefixed with `!`): Exclude matching modules
- Wildcard support: `*` for any substring
- Regex support: Full regex patterns for complex filtering

### Call Stack Management

**Nested Call Tracking**:
```python
class CallStackManager:
    def __init__(self):
        self.stack = []
        self.max_depth = 0
        self.call_counts = defaultdict(int)

    def enter_call(self, call_event):
        self.stack.append(call_event)
        self.max_depth = max(self.max_depth, len(self.stack))
        self.call_counts[call_event.function_name] += 1

    def exit_call(self, return_event):
        if self.stack:
            call_event = self.stack.pop()
            call_event.return_value = return_event.return_value
            return call_event
```

### Performance Metrics Collection

**Automatic Performance Tracking**:
```python
class PerformanceTracker:
    def collect_metrics(self, trace_events):
        return {
            "total_execution_time": self._calculate_total_time(trace_events),
            "function_call_counts": self._count_function_calls(trace_events),
            "max_call_depth": self._find_max_depth(trace_events),
            "hot_spots": self._identify_performance_hotspots(trace_events),
            "memory_usage": self._track_memory_consumption(trace_events)
        }
```

## Integration Patterns

### pytest Integration

**Fixture-Based Tracing**:
```python
@pytest.fixture
def function_tracer():
    tracer = FunctionTracer(filter_modules=["myapp.*"])
    yield tracer
    tracer.cleanup()

def test_with_tracing(function_tracer, snapshot):
    with function_tracer:
        result = business_function(test_input)

    execution_summary = {
        "result": result,
        "call_trace": function_tracer.format_events(),
        "metrics": function_tracer.get_metrics()
    }

    assert execution_summary == snapshot
```

**Parameterized Trace Testing**:
```python
@pytest.mark.parametrize("trace_level", ["minimal", "detailed", "verbose"])
def test_different_trace_levels(trace_level, snapshot):
    tracer = FunctionTracer(detail_level=trace_level)

    with tracer:
        result = complex_algorithm(test_data)

    assert tracer.format_trace() == snapshot
```

### Syrupy Integration

**Custom Snapshot Extensions**:
```python
class TracedSnapshotExtension(SnapshotExtension):
    def serialize(self, data, **kwargs):
        if isinstance(data, TracedExecution):
            return self._serialize_traced_execution(data)
        return super().serialize(data, **kwargs)

    def _serialize_traced_execution(self, traced):
        return {
            "function_calls": [self._serialize_call(call) for call in traced.calls],
            "call_graph": traced.build_call_graph(),
            "performance_summary": traced.get_performance_summary()
        }
```

### Legacy Code Integration

**Non-Invasive Tracing**:
```python
def trace_legacy_system(legacy_function, *args, **kwargs):
    """Trace legacy code without modification"""
    tracer = FunctionTracer()

    with tracer:
        result = legacy_function(*args, **kwargs)

    return {
        "result": result,
        "execution_flow": tracer.get_execution_flow(),
        "called_functions": tracer.get_function_list(),
        "performance_data": tracer.get_timing_data()
    }
```

## Advanced Usage Patterns

### Recursive Function Tracing

**Handling Recursive Calls**:
```python
class RecursiveTracker:
    def __init__(self):
        self.recursion_depth = 0
        self.recursion_patterns = {}

    def track_recursive_call(self, function_name, args):
        if function_name in self.recursion_patterns:
            self.recursion_patterns[function_name].append({
                "depth": self.recursion_depth,
                "args": args,
                "timestamp": time.time()
            })
        else:
            self.recursion_patterns[function_name] = []
```

### Asynchronous Function Tracing

**Async/Await Support**:
```python
class AsyncTracer(FunctionTracer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.async_tasks = {}
        self.task_call_stacks = defaultdict(list)

    async def trace_async_function(self, async_func, *args, **kwargs):
        task_id = asyncio.current_task().get_name()

        with self.trace_context(task_id):
            result = await async_func(*args, **kwargs)

        return result
```

### Memory-Efficient Large System Tracing

**Streaming Trace Processing**:
```python
class StreamingTracer(FunctionTracer):
    def __init__(self, buffer_size=10000):
        super().__init__()
        self.buffer_size = buffer_size
        self.event_buffer = []
        self.trace_processor = TraceProcessor()

    def add_event(self, event):
        self.event_buffer.append(event)

        if len(self.event_buffer) >= self.buffer_size:
            self.trace_processor.process_batch(self.event_buffer)
            self.event_buffer.clear()
```

## Testing Strategies

### Unit Testing the Tracer

```python
def test_function_tracer_captures_calls():
    tracer = FunctionTracer()

    def test_function(x, y):
        return x + y

    with tracer:
        result = test_function(1, 2)

    events = tracer.get_events()
    assert len(events) == 2  # call and return
    assert events[0].event_type == 'call'
    assert events[0].function_name == 'test_function'
    assert events[0].args == {'x': 1, 'y': 2}
    assert events[1].return_value == 3
```

### Integration Testing with Syrupy

```python
def test_traced_snapshot_integration(snapshot):
    def complex_workflow(data):
        processed = preprocess_data(data)
        validated = validate_data(processed)
        return finalize_data(validated)

    traced = TracedSnapshot()
    with traced:
        result = complex_workflow(test_data)

    # Comprehensive snapshot including execution trace
    full_context = {
        "input": test_data,
        "output": result,
        "execution_trace": traced.format_trace(),
        "function_calls": traced.get_function_calls(),
        "call_graph": traced.build_call_graph()
    }

    assert full_context == snapshot
```

### Performance Testing

```python
def test_tracer_performance_overhead():
    def benchmark_function():
        # Representative workload
        return sum(range(10000))

    # Measure without tracing
    start_time = time.perf_counter()
    for _ in range(100):
        benchmark_function()
    baseline_time = time.perf_counter() - start_time

    # Measure with tracing
    tracer = FunctionTracer()
    start_time = time.perf_counter()
    with tracer:
        for _ in range(100):
            benchmark_function()
    traced_time = time.perf_counter() - start_time

    # Overhead should be minimal (< 5%)
    overhead_percent = (traced_time - baseline_time) / baseline_time * 100
    assert overhead_percent < 5.0
```

## Error Handling and Diagnostics

### Trace Validation

```python
class TraceValidator:
    def validate_call_balance(self, events):
        """Ensure every call has a matching return"""
        call_stack = []
        for event in events:
            if event.event_type == 'call':
                call_stack.append(event)
            elif event.event_type == 'return':
                if not call_stack:
                    raise TraceError("Return without matching call")
                call_stack.pop()

        if call_stack:
            raise TraceError("Unmatched function calls")
```

### Performance Diagnostics

```python
class TracingDiagnostics:
    def analyze_performance_impact(self, tracer):
        metrics = tracer.get_performance_metrics()

        report = {
            "overhead_percentage": metrics.calculate_overhead(),
            "memory_usage_mb": metrics.get_memory_usage() / 1024 / 1024,
            "events_per_second": metrics.get_event_rate(),
            "bottlenecks": metrics.identify_bottlenecks()
        }

        return report
```

This comprehensive coverage of snapy_testing enables deep understanding of the function tracing framework and its integration with modern Python testing workflows.