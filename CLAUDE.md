# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PySnap is a Python testing framework with two main components:
1. **snapy_capture** - Automatic function argument capture for replay testing
2. **snapy_testing** - Enhanced snapshot testing with function tracing

The project enables developers to capture real function arguments during execution and replay them in tests, combined with comprehensive function call tracing for validation.

## Development Commands

### Dependencies and Environment
```bash
# Install dependencies (requires Poetry to be installed first)
poetry install

# Activate virtual environment
poetry shell

# Run with system Python if Poetry unavailable
python3 -m pip install syrupy pytest
```

### Testing
```bash
# Run all tests
python3 -m pytest

# Run specific test modules
python3 -m pytest src/snapy_capture/tests/
python3 -m pytest src/snapy_testing/

# Run with specific Python path
PYTHONPATH=src python3 -m pytest

# Run individual test files
PYTHONPATH=src python3 tests/test_tracer.py
PYTHONPATH=src python3 tests/test_integration.py
```

### Examples and Development
```bash
# Run capture examples
cd src/snapy_capture/examples
python3 basic_usage.py
python3 test_with_captures.py

# Run enhanced examples
PYTHONPATH=. python3 enhanced_snap_test.py
```

## Architecture

### Core Components

**snapy_capture/** - Argument capture system
- `capture.py` - Main `@capture_args()` decorator
- `storage.py` - Pickle-based argument storage
- `config.py` - Configuration management via environment variables
- `filters.py` - Argument filtering for security (passwords, tokens)
- `loader.py` - Loading captured arguments for replay

**snapy_testing/** - Function tracing system
- `tracer.py` - `FunctionTracer` using `sys.settrace`
- `snapshot.py` - `TracedSnapshot` for syrupy integration
- `decorators.py` - Higher-level tracing decorators (WIP)
- `context.py` - Context managers for tracing (WIP)

### Key Patterns

**Decorator-Based Capture**
```python
from snapy_capture import capture_args

@capture_args(path="./captures", retention=2)
def business_function(user_id, data, secret=None):
    return process_data(user_id, data)
```

**Test Replay Pattern**
```python
from snapy_capture import load_capture

def test_business_function(snapshot):
    args, kwargs = load_capture("business_function")
    result = business_function(*args, **kwargs)
    assert result == snapshot
```

**Function Tracing**
```python
from snapy_testing import FunctionTracer

tracer = FunctionTracer()
with tracer:
    result = complex_function()
events = tracer.get_events()  # All function calls captured
```

### Configuration

**Environment Variables** (copy .env.example to .env):
- `SNAP_CAPTURE_ENABLED=true` - Global enable/disable
- `SNAP_CAPTURE_DEFAULT_PATH=./snap_capture` - Storage location
- `SNAP_CAPTURE_DEFAULT_RETENTION=2` - Number of captures to keep
- `SNAP_CAPTURE_IGNORE_ARGS=password,token,secret,key` - Filtered arguments

**Production Settings**:
- `SNAP_CAPTURE_PRODUCTION_MODE=true` - Minimal overhead mode
- `SNAP_CAPTURE_MINIMAL=true` - Essential data only

### Project Structure

```
src/
├── snapy_capture/          # Argument capture framework
│   ├── examples/           # Comprehensive usage examples
│   └── tests/              # Unit tests for capture system
├── snapy_testing/          # Function tracing framework
│   └── advanced/           # Advanced tracing features (WIP)
└── __snapshots__/          # Syrupy snapshot files
```

### Dependencies

- **syrupy** - Snapshot testing framework (>= 4.9.1)
- **pytest** - Testing framework (>= 8.4.2)
- Built for Python >= 3.11

### Security Considerations

The capture system automatically filters sensitive arguments by name patterns. Always review captured data and extend filtering for your specific security requirements.

Default filtered arguments: password, token, secret, key, auth, api_key, access_token, refresh_token