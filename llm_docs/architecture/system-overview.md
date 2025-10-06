# PySnap System Architecture Overview

## Framework Architecture

PySnap implements a dual-framework approach to comprehensive Python testing through two interconnected but independent systems:

### 1. snapy_capture: Argument Capture Framework
**Purpose**: Captures function arguments during execution for replay in tests
**Core Pattern**: Decorator-based interception with configurable storage
**Key Innovation**: Production-safe argument capture with security filtering

```
@capture_args() → Function Execution → Argument Storage → Test Replay
```

### 2. snapy_testing: Function Tracing Framework
**Purpose**: Traces complete function execution flow with nested call capture
**Core Pattern**: sys.settrace-based instrumentation with syrupy integration
**Key Innovation**: Complete execution context capture for validation

```
FunctionTracer → sys.settrace → CallEvent Stream → TracedSnapshot → Syrupy
```

## Architectural Principles

### Separation of Concerns
- **Capture**: Focuses solely on argument preservation and replay
- **Tracing**: Handles execution flow and behavior validation
- **Storage**: Isolated serialization and persistence layer
- **Configuration**: Centralized environment-based settings

### Production Safety
- **Non-invasive Design**: Zero impact when disabled
- **Security First**: Automatic filtering of sensitive data
- **Performance Conscious**: Minimal overhead through lazy evaluation
- **Graceful Degradation**: Function execution continues even if capture fails

### Composability
- **Independent Operation**: Each framework works standalone
- **Synergistic Integration**: Combined usage provides comprehensive testing
- **Plugin Architecture**: Extensible through custom filters and serializers
- **Framework Agnostic**: Works with any testing framework (pytest, unittest, etc.)

## Data Flow Architecture

### Capture Flow
```
Function Call → Decorator Interception → Filter Chain → Serialization → Storage
     ↓
Test Execution → Load Capture → Deserialize → Replay Function → Validate
```

### Tracing Flow
```
Function Entry → sys.settrace → Event Generation → Call Stack Management
     ↓
Event Stream → TracedSnapshot → Syrupy Integration → Snapshot Validation
```

## Component Interaction

### Internal Communication
- **Configuration System**: Shared environment variable management
- **Storage Layer**: Common serialization patterns
- **Filter System**: Reusable security and performance filters
- **Error Handling**: Consistent failure modes and recovery

### External Integration
- **pytest**: Primary testing framework integration
- **syrupy**: Snapshot testing library for assertions
- **pickle**: Serialization backend for argument storage
- **sys.settrace**: Core Python tracing mechanism

## Design Patterns

### Decorator Pattern
Central to argument capture with configurable behavior:
```python
@capture_args(path="./captures", retention=5, ignore_args=["password"])
def business_function(user_id, data, password=None):
    return process_data(user_id, data)
```

### Observer Pattern
Implemented in function tracing for event notification:
```python
tracer = FunctionTracer(filter_modules=["myapp.*"])
with tracer:
    # All function calls observed and recorded
    result = complex_business_logic()
```

### Strategy Pattern
Configuration-driven behavior modification:
```python
# Production strategy
config = CaptureConfig(production_mode=True, minimal_capture=True)

# Development strategy
config = CaptureConfig(full_capture=True, debug_mode=True)
```

### Adapter Pattern
Bridges between legacy code and modern testing:
```python
# Adapter enables testing of untestable legacy code
def test_legacy_system(snapshot):
    args, kwargs = load_capture("legacy_function")
    result = legacy_function(*args, **kwargs)
    assert result == snapshot
```

## Security Architecture

### Multi-Layer Protection
1. **Configuration Level**: Environment variables for global filtering
2. **Decorator Level**: Function-specific argument exclusion
3. **Filter Level**: Pattern-based automatic detection
4. **Storage Level**: Encrypted serialization options

### Default Security Filters
```python
SENSITIVE_PATTERNS = [
    "password", "token", "secret", "key", "auth",
    "api_key", "access_token", "refresh_token"
]
```

### Production Hardening
- **Minimal Capture Mode**: Essential data only
- **Automatic Cleanup**: Configurable retention policies
- **Access Control**: File permission management
- **Audit Logging**: Capture event tracking

## Performance Architecture

### Lazy Evaluation
- **Deferred Serialization**: Serialize only when needed
- **Streaming Storage**: Handle large datasets efficiently
- **Memory Management**: Circular buffers prevent unbounded growth

### Optimization Strategies
- **Sampling**: Configurable capture frequency
- **Filtering**: Early elimination of irrelevant data
- **Caching**: Reuse expensive operations
- **Profiling**: Built-in performance monitoring

## Extensibility Points

### Custom Filters
```python
class CustomArgumentFilter(ArgumentFilter):
    def should_capture(self, arg_name, arg_value):
        # Custom filtering logic
        return not self._is_sensitive(arg_name, arg_value)
```

### Custom Storage
```python
class DatabaseStorage(CaptureStorage):
    def store_capture(self, function_name, args, kwargs):
        # Store in database instead of files
        pass
```

### Custom Serializers
```python
class JSONSerializer:
    def serialize(self, data):
        return json.dumps(data, cls=CustomJSONEncoder)
```

## Framework Integration

### pytest Integration
- **Fixtures**: Automatic capture loading
- **Markers**: Test categorization and filtering
- **Hooks**: Custom test lifecycle integration
- **Parametrization**: Multiple capture replay

### syrupy Integration
- **TracedSnapshot**: Custom snapshot class
- **Filters**: Syrupy-compatible data filtering
- **Serialization**: Multiple output formats
- **Assertions**: Enhanced comparison logic

This architecture enables PySnap to provide comprehensive testing capabilities while maintaining production safety, performance, and extensibility.