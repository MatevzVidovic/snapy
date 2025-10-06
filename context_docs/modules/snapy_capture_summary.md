# snapy_capture Module Summary

## Core Purpose
Automatic function argument capture for replay testing without manual test data creation.

## Key Files

### capture.py
- **Main export**: `@capture_args()` decorator
- **Function**: Intercepts function calls, captures arguments
- **Features**: Thread-safe, async support, configurable filtering
- **Usage**: `@capture_args(path="./captures", ignore_args=["password"])`

### storage.py
- **Main export**: `CaptureStorage` class
- **Function**: Pickle-based argument persistence with retention
- **Features**: Atomic writes, cleanup policies, thread-safe file operations
- **Format**: `{function_name, timestamp, args, kwargs, metadata}`

### config.py
- **Main export**: `CaptureConfig` class
- **Function**: Environment-based configuration management
- **Key vars**: `SNAP_CAPTURE_ENABLED`, `SNAP_CAPTURE_DEFAULT_PATH`
- **Modes**: Development vs production optimization

### filters.py
- **Main export**: `ArgumentFilter` class
- **Function**: Security filtering of sensitive arguments
- **Patterns**: Automatic detection of passwords, tokens, PII
- **Extensible**: Custom filter functions and patterns

### loader.py
- **Main export**: `load_capture()`, `CaptureLoader`
- **Function**: Load captured arguments for test replay
- **Features**: Multiple selection strategies, fallback handling
- **Integration**: Direct pytest parametrization support

## Usage Pattern

### Development
```python
# 1. Add decorator to function
@capture_args()
def business_function(user_id, data):
    return process_data(user_id, data)

# 2. Run function normally (captures arguments)
result = business_function("user123", {"key": "value"})

# 3. Use in tests
def test_business_function(snapshot):
    args, kwargs = load_capture("business_function")
    result = business_function(*args, **kwargs)
    assert result == snapshot
```

### Production Configuration
```python
# .env file
SNAP_CAPTURE_ENABLED=true
SNAP_CAPTURE_PRODUCTION_MODE=true
SNAP_CAPTURE_IGNORE_ARGS=password,token,secret,api_key
SNAP_CAPTURE_DEFAULT_RETENTION=1
```

## Common Commands
```bash
# Generate captures
python3 src/snapy_capture/examples/basic_usage.py

# Run tests with captures
python3 -m pytest tests/ -k "capture"

# Check capture files
ls ./snap_capture/
```

## Integration Points
- **pytest**: Fixtures, parametrization, test data management
- **Legacy code**: Non-invasive retrofitting with decorators
- **CI/CD**: Environment-based enable/disable for different stages
- **Security**: Automatic filtering prevents sensitive data capture