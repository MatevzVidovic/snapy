# Common PySnap Development Workflows

## Testing Workflows

### Running Tests
```bash
# All tests
python3 -m pytest

# With PYTHONPATH (recommended)
PYTHONPATH=src python3 -m pytest

# Specific test modules
python3 -m pytest src/snapy_capture/tests/
python3 -m pytest src/snapy_testing/

# Individual test files
PYTHONPATH=src python3 tests/test_tracer.py
PYTHONPATH=src python3 tests/test_integration.py
```

### Example Execution
```bash
# Capture examples
cd src/snapy_capture/examples
python3 basic_usage.py           # Basic capture patterns
python3 test_with_captures.py    # Test integration
python3 production_example.py    # Production config

# Enhanced examples
cd ../../..
PYTHONPATH=. python3 enhanced_snap_test.py
```

## Development Patterns

### Adding New Functions with Capture
```python
# 1. Add capture decorator
@capture_args(ignore_args=["sensitive_data"])
def new_business_function(user_id, data, sensitive_data=None):
    return process_business_logic(user_id, data)

# 2. Execute function to generate captures
result = new_business_function("test_user", {"key": "value"})

# 3. Create test using captured data
def test_new_business_function(snapshot):
    args, kwargs = load_capture("new_business_function")
    result = new_business_function(*args, **kwargs)
    assert result == snapshot
```

### Testing Complex Workflows
```python
# 1. Identify workflow to test
def complex_workflow(input_data):
    step1 = preprocess(input_data)
    step2 = validate(step1)
    step3 = transform(step2)
    return finalize(step3)

# 2. Add tracing to test
def test_complex_workflow(snapshot):
    tracer = FunctionTracer(filter_modules=["myapp.*"])

    with tracer:
        result = complex_workflow(test_data)

    # Capture both result and execution flow
    assert {
        "result": result,
        "execution_flow": tracer.format_trace(),
        "performance": tracer.get_metrics()
    } == snapshot
```

### Legacy Code Integration
```python
# 1. Identify legacy function to test
def legacy_function(complex_args):
    # Untestable legacy code
    pass

# 2. Add capture decorator non-invasively
legacy_function = capture_args(
    path="./legacy_captures",
    ignore_args=["sensitive_field"]
)(legacy_function)

# 3. Generate captures by running legacy code
result = legacy_function(production_like_data)

# 4. Create characterization test
def test_legacy_behavior(snapshot):
    args, kwargs = load_capture("legacy_function")
    result = legacy_function(*args, **kwargs)
    assert result == snapshot  # Documents current behavior
```

## Configuration Workflows

### Development Environment Setup
```bash
# 1. Copy environment template
cp .env.example .env

# 2. Configure for development
SNAP_CAPTURE_ENABLED=true
SNAP_CAPTURE_DEFAULT_PATH=./dev_captures
SNAP_CAPTURE_DEFAULT_RETENTION=5
```

### Production Environment Setup
```bash
# 1. Configure for production safety
SNAP_CAPTURE_ENABLED=true
SNAP_CAPTURE_PRODUCTION_MODE=true
SNAP_CAPTURE_MINIMAL=true
SNAP_CAPTURE_DEFAULT_RETENTION=1
SNAP_CAPTURE_IGNORE_ARGS=password,token,secret,api_key,credentials
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Run PySnap tests
  env:
    SNAP_CAPTURE_ENABLED: false  # Disable capture in CI
  run: |
    PYTHONPATH=src python3 -m pytest
```

## Debugging Workflows

### Capture Issues
```python
# Check if captures exist
from snapy_capture import has_capture, capture_count

if not has_capture("function_name"):
    print("No captures found - run function first")

print(f"Available captures: {capture_count('function_name')}")
```

### Trace Analysis
```python
# Analyze performance bottlenecks
def analyze_performance():
    tracer = FunctionTracer()
    with tracer:
        slow_function()

    metrics = tracer.get_metrics()
    events = tracer.get_events()

    # Find slow functions
    slow_functions = [e for e in events if e.duration and e.duration > 0.1]
    print(f"Slow functions: {slow_functions}")
```

### Storage Management
```bash
# Check capture storage usage
ls -la ./snap_capture/

# Clean up old captures
python3 -c "
from snapy_capture import CaptureLoader
loader = CaptureLoader()
stats = loader.get_storage_stats()
print(f'Storage usage: {stats}')
loader.cleanup_all_captures(retention=1)
"
```

## Integration Workflows

### Combined Capture + Tracing
```python
def test_comprehensive_workflow(snapshot):
    # 1. Load real arguments from capture
    args, kwargs = load_capture("business_function")

    # 2. Trace execution with real data
    tracer = FunctionTracer()
    with tracer:
        result = business_function(*args, **kwargs)

    # 3. Comprehensive validation
    complete_test = {
        "input_args": {"args": args, "kwargs": kwargs},
        "result": result,
        "execution_trace": tracer.format_trace(),
        "performance_metrics": tracer.get_metrics(),
        "call_graph": tracer.get_call_graph()
    }

    assert complete_test == snapshot
```

### Syrupy Snapshot Updates
```bash
# Update snapshots when behavior changes
python3 -m pytest --snapshot-update

# Update specific test snapshots
python3 -m pytest tests/test_specific.py --snapshot-update
```

These workflows cover the most common development patterns and tasks when working with PySnap.