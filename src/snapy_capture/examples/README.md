# Snapy Capture Examples

This directory contains comprehensive examples demonstrating how to use snapy_capture for automatic function argument capture and replay testing.

## Examples Overview

### 1. `basic_usage.py`
**Basic argument capture patterns**
- Simple `@capture_args()` decorator usage
- Custom storage paths and retention policies
- Argument filtering for sensitive data
- Multiple function examples with different configurations

**Run it:**
```bash
python basic_usage.py
```

### 2. `test_with_captures.py`
**Testing with captured arguments**
- Loading captured arguments in pytest tests
- Snapshot testing with syrupy
- Parametrized tests using multiple captures
- Pytest fixtures for capture loading
- Fallback to manual arguments when captures don't exist

**Run it:**
```bash
python test_with_captures.py
```

### 3. `integration_with_snapy_testing.py`
**Integration with snapy_testing framework**
- Combining argument capture with function tracing
- Comprehensive testing using both approaches
- Complex business logic examples
- Demonstrates the power of combined capture + trace testing

**Run it:**
```bash
python integration_with_snapy_testing.py
```

### 4. `production_example.py`
**Production-ready usage patterns**
- Production-safe configuration
- Performance monitoring and optimization
- Minimal capture mode for high-frequency functions
- Error handling and graceful degradation
- Security best practices

**Run it:**
```bash
python production_example.py
```

## Quick Start

1. **Generate some captures:**
   ```bash
   cd src/snapy_capture/examples
   python basic_usage.py
   ```

2. **Run tests with captures:**
   ```bash
   python test_with_captures.py
   ```

3. **See advanced integration:**
   ```bash
   python integration_with_snapy_testing.py
   ```

## Key Concepts Demonstrated

### Argument Capture
```python
from snapy_capture import capture_args

@capture_args()
def my_function(arg1, arg2, secret=None):
    return f"{arg1}-{arg2}"

# Arguments automatically captured when called
result = my_function("hello", "world", secret="filtered")
```

### Loading Captures in Tests
```python
from snapy_capture import load_capture

def test_my_function(snapshot):
    # Load captured arguments
    args, kwargs = load_capture("my_function")

    # Replay function call
    result = my_function(*args, **kwargs)

    # Use snapshot testing
    assert result == snapshot
```

### Production Configuration
```python
from snapy_capture.config import CaptureConfig, set_global_config

# Production-safe setup
config = CaptureConfig()
config.production_mode = True
config.minimal_capture = True
config.ignore_args.extend(['password', 'api_key', 'token'])
set_global_config(config)
```

### Integration with Tracing
```python
from snapy_capture import load_capture
from snapy_testing import create_traced_snapshot

def test_with_capture_and_trace(snapshot):
    # Load real arguments
    args, kwargs = load_capture("business_function")

    # Trace execution
    traced = create_traced_snapshot()
    result = traced.capture_trace(business_function, *args, **kwargs)

    # Test both result and execution flow
    combined = {
        "result": result,
        "trace": traced.format_trace()
    }
    assert combined == snapshot
```

## Configuration Examples

### Environment Variables (.env)
```bash
# Enable/disable capture
SNAP_CAPTURE_ENABLED=true

# Storage configuration
SNAP_CAPTURE_DEFAULT_PATH=./captures
SNAP_CAPTURE_DEFAULT_RETENTION=2

# Security filtering
SNAP_CAPTURE_IGNORE_ARGS=password,token,secret,api_key

# Production optimization
SNAP_CAPTURE_PRODUCTION_MODE=true
SNAP_CAPTURE_MINIMAL=true
```

### Programmatic Configuration
```python
from snapy_capture import capture_args, CaptureContext

# Function-level configuration
@capture_args(
    path="./special_captures",
    retention=5,
    ignore_args=["sensitive_data"],
    overwrite=True
)
def configured_function(data, sensitive_data=None):
    return process(data)

# Context-based configuration
with CaptureContext(enabled=False):
    # No captures in this block
    configured_function(test_data)

with CaptureContext(path="./debug_captures"):
    # Use different path in this block
    configured_function(debug_data)
```

## Testing Patterns

### Basic Test Pattern
```python
def test_function_with_captures(snapshot):
    if has_capture("function_name"):
        args, kwargs = load_capture("function_name")
        result = function_name(*args, **kwargs)
    else:
        # Fallback to manual test data
        result = function_name("test", "data")

    assert result == snapshot
```

### Parametrized Testing
```python
@pytest.mark.parametrize("capture_index", [0, 1, 2])
def test_multiple_captures(capture_index, snapshot):
    loader = CaptureLoader()
    args, kwargs = loader.load_by_index("function_name", capture_index)
    result = function_name(*args, **kwargs)
    assert result == snapshot
```

### Fixture-Based Testing
```python
@pytest.fixture
def captured_args():
    return load_capture("function_name")

def test_with_fixture(captured_args, snapshot):
    args, kwargs = captured_args
    result = function_name(*args, **kwargs)
    assert result == snapshot
```

## Best Practices

### Development
- Use full capture mode for comprehensive testing
- Capture arguments from real usage scenarios
- Combine with function tracing for complete coverage

### Staging
- Use moderate filtering to balance detail and performance
- Test production configurations before deployment
- Validate capture/replay consistency

### Production
- Enable production mode and minimal capture
- Filter all sensitive arguments
- Monitor performance impact
- Implement graceful degradation for capture failures

### Security
- Always filter passwords, tokens, API keys
- Review captured data regularly
- Use appropriate file permissions for capture storage
- Consider data retention policies for compliance

## Troubleshooting

### No Captures Found
```python
# Check if captures exist
from snapy_capture import has_capture
if not has_capture("function_name"):
    print("No captures found - run the function first")
```

### Capture Failures
```python
# Captures fail gracefully - function still works
@capture_args()
def robust_function(data):
    return process(data)  # Always works regardless of capture status
```

### Performance Issues
```python
# Use minimal capture for high-frequency functions
from snapy_capture import capture_minimal

@capture_minimal()
def high_frequency_function(data):
    return fast_process(data)
```

### Storage Management
```python
# Clean up old captures
from snapy_capture import CaptureLoader
loader = CaptureLoader()
stats = loader.get_storage_stats()
print(f"Total storage: {stats['total_size_bytes']} bytes")

# Delete old captures
loader.cleanup_all_captures(retention=1)
```

## Next Steps

1. Try the examples in order: basic → testing → integration → production
2. Adapt the patterns to your specific use cases
3. Set up appropriate configuration for your environment
4. Integrate with your existing test suite
5. Monitor performance and adjust settings as needed

For more details, see the main documentation and API reference.