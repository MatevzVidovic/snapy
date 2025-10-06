# snapy_capture Module Documentation

## Overview

The snapy_capture module provides automatic function argument capture and replay capabilities for Python testing. It uses decorator-based interception to capture function arguments during execution and stores them for later replay in tests.

## Core Components

### 1. capture.py - Main Decorator System

**Primary Function**: `@capture_args()` decorator
- Intercepts function calls at execution time
- Captures arguments with configurable filtering
- Handles both synchronous and asynchronous functions
- Provides graceful degradation on capture failures

**Key Features**:
- Thread-safe operation using threading.local()
- Support for nested and recursive function calls
- Configurable storage paths and retention policies
- Argument filtering for security and performance

**Example Usage**:
```python
@capture_args(path="./captures", retention=3, ignore_args=["password"])
def user_authentication(username, password, remember_me=False):
    return authenticate_user(username, password, remember_me)
```

**Implementation Details**:
- Uses functools.wraps to preserve function metadata
- Employs inspect module for argument introspection
- Handles asyncio coroutines with async/await pattern
- Maintains call depth tracking for nested calls

### 2. storage.py - Persistence Layer

**Primary Class**: `CaptureStorage`
- Manages pickle-based argument serialization
- Implements retention policy enforcement
- Provides atomic file operations for thread safety
- Handles storage cleanup and garbage collection

**Key Features**:
- Atomic write operations prevent corruption
- Configurable retention policies (count-based and time-based)
- Automatic cleanup of expired captures
- Thread-safe file locking mechanisms

**Storage Format**:
```python
{
    "function_name": "user_authentication",
    "timestamp": "2023-09-15T10:30:00Z",
    "args": ["john_doe"],
    "kwargs": {"remember_me": True},
    "metadata": {
        "call_depth": 0,
        "thread_id": "MainThread",
        "python_version": "3.11.4"
    }
}
```

### 3. config.py - Configuration Management

**Primary Class**: `CaptureConfig`
- Environment variable integration
- Default value management
- Production vs development mode settings
- Security configuration enforcement

**Configuration Sources** (priority order):
1. Function decorator parameters
2. Environment variables
3. Global configuration object
4. Built-in defaults

**Key Environment Variables**:
- `SNAP_CAPTURE_ENABLED`: Global enable/disable
- `SNAP_CAPTURE_DEFAULT_PATH`: Storage directory
- `SNAP_CAPTURE_DEFAULT_RETENTION`: Number of captures to keep
- `SNAP_CAPTURE_IGNORE_ARGS`: Comma-separated sensitive argument names
- `SNAP_CAPTURE_PRODUCTION_MODE`: Enables production optimizations

### 4. filters.py - Security and Performance Filtering

**Primary Class**: `ArgumentFilter`
- Pattern-based argument exclusion
- Type-based filtering for performance
- Nested object traversal and sanitization
- Custom filter extension points

**Default Security Filters**:
```python
SENSITIVE_PATTERNS = [
    "password", "token", "secret", "key", "auth",
    "api_key", "access_token", "refresh_token",
    "session_id", "csrf_token", "oauth_token"
]
```

**Filter Types**:
- **Name-based**: Filter by argument name patterns
- **Value-based**: Filter by argument value content
- **Type-based**: Filter by Python type (e.g., large objects)
- **Size-based**: Filter arguments exceeding size limits

### 5. loader.py - Capture Retrieval System

**Primary Functions**:
- `load_capture(function_name)`: Load most recent capture
- `load_capture_dict(function_name)`: Load as dictionary format
- `CaptureLoader`: Advanced loading with filtering and selection

**Key Features**:
- Multiple capture selection strategies
- Automatic fallback handling for missing captures
- Integration with pytest parametrization
- Batch loading for performance

**Usage Patterns**:
```python
# Basic loading
args, kwargs = load_capture("user_authentication")

# Advanced loading with selection
loader = CaptureLoader()
captures = loader.load_all("user_authentication")
args, kwargs = loader.select_by_criteria(captures, {"thread_id": "MainThread"})
```

## Integration Patterns

### pytest Integration

**Fixture-based Loading**:
```python
@pytest.fixture
def captured_user_args():
    return load_capture("user_authentication")

def test_authentication(captured_user_args, snapshot):
    args, kwargs = captured_user_args
    result = user_authentication(*args, **kwargs)
    assert result == snapshot
```

**Parametrized Testing**:
```python
@pytest.mark.parametrize("capture_index", range(3))
def test_multiple_scenarios(capture_index, snapshot):
    loader = CaptureLoader()
    args, kwargs = loader.load_by_index("payment_processing", capture_index)
    result = payment_processing(*args, **kwargs)
    assert result == snapshot
```

### Production Deployment

**Safe Production Configuration**:
```python
# In production environment
config = CaptureConfig(
    production_mode=True,
    minimal_capture=True,
    ignore_large_objects=True,
    max_capture_size=1024,  # 1KB limit
    retention=1  # Keep only latest
)
set_global_config(config)
```

### Legacy Code Integration

**Retrofitting Existing Functions**:
```python
# Original legacy function
def legacy_payment_processor(card_data, amount, merchant_id):
    # Complex legacy logic
    return process_payment_legacy(card_data, amount, merchant_id)

# Add capture capability without modifying internals
legacy_payment_processor = capture_args(
    path="./legacy_captures",
    ignore_args=["card_data"]  # Security filtering
)(legacy_payment_processor)
```

## Advanced Features

### Custom Serialization

**Implementing Custom Serializers**:
```python
class JSONCaptureStorage(CaptureStorage):
    def serialize_data(self, data):
        return json.dumps(data, cls=CustomJSONEncoder, indent=2)

    def deserialize_data(self, data):
        return json.loads(data)
```

### Performance Optimization

**High-Performance Capture**:
```python
@capture_args(
    lazy_serialization=True,
    sample_rate=0.1,  # Capture 10% of calls
    async_storage=True
)
def high_frequency_function(data):
    return process_data(data)
```

### Security Hardening

**Enhanced Security Configuration**:
```python
class SecureArgumentFilter(ArgumentFilter):
    def __init__(self):
        super().__init__()
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{16}\b',              # Credit card pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]

    def contains_pii(self, value):
        if isinstance(value, str):
            for pattern in self.pii_patterns:
                if re.search(pattern, value):
                    return True
        return False
```

## Testing Strategies

### Unit Testing the Capture System

```python
def test_capture_filtering():
    @capture_args(ignore_args=["secret"])
    def test_function(public_data, secret):
        return {"data": public_data}

    # Execute function with sensitive data
    result = test_function("public", "sensitive")

    # Verify capture exists and is filtered
    args, kwargs = load_capture("test_function")
    assert "sensitive" not in str(args) + str(kwargs)
```

### Integration Testing

```python
def test_end_to_end_capture_replay():
    # Step 1: Execute function with capture
    original_result = user_service.create_user(
        username="testuser",
        email="test@example.com",
        password="secret123"
    )

    # Step 2: Load captured arguments
    args, kwargs = load_capture("create_user")

    # Step 3: Replay and validate
    replayed_result = user_service.create_user(*args, **kwargs)

    # Results should be identical (excluding dynamic fields)
    assert original_result["username"] == replayed_result["username"]
    assert original_result["email"] == replayed_result["email"]
```

## Error Handling and Troubleshooting

### Common Issues

**Capture Not Found**:
```python
try:
    args, kwargs = load_capture("function_name")
except CaptureNotFoundError:
    # Fallback to manual test data
    args, kwargs = get_test_data("function_name")
```

**Serialization Failures**:
```python
@capture_args(
    fallback_serializer=JSONPickleSerializer(),
    ignore_serialization_errors=True
)
def function_with_complex_objects(data):
    return process_complex_data(data)
```

**Performance Issues**:
```python
# Monitor capture performance
with CaptureProfiler() as profiler:
    result = expensive_function(large_data)

print(f"Capture overhead: {profiler.capture_time_ms}ms")
print(f"Serialization size: {profiler.serialized_size_bytes} bytes")
```

This comprehensive coverage of snapy_capture enables deep understanding of the argument capture framework and its integration patterns.