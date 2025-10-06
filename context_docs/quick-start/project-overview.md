# PySnap Quick Start

## What is PySnap?

PySnap is a dual-framework Python testing system that captures function arguments during execution and traces complete function execution flows for comprehensive testing.

## Core Concepts

### snapy_capture
- **Purpose**: Capture function arguments automatically for test replay
- **Pattern**: `@capture_args()` decorator → argument storage → test loading
- **Security**: Automatic filtering of sensitive data (passwords, tokens)
- **Storage**: Pickle-based serialization in configurable directories

### snapy_testing
- **Purpose**: Trace function execution with sys.settrace
- **Pattern**: `FunctionTracer()` → execution events → `TracedSnapshot` → syrupy
- **Output**: Complete call graphs, performance metrics, execution flows
- **Integration**: Works seamlessly with existing pytest/syrupy workflows

## 5-Minute Usage

### Capture Arguments
```python
from snapy_capture import capture_args

@capture_args()
def process_user(user_id, data, password=None):
    return {"processed": True, "user": user_id}

# Arguments automatically captured when called
result = process_user("user123", {"key": "value"}, password="secret")
```

### Replay in Tests
```python
from snapy_capture import load_capture

def test_process_user(snapshot):
    args, kwargs = load_capture("process_user")
    result = process_user(*args, **kwargs)
    assert result == snapshot
```

### Trace Execution
```python
from snapy_testing import FunctionTracer

def test_complex_workflow(snapshot):
    tracer = FunctionTracer()
    with tracer:
        result = complex_business_logic()

    assert {
        "result": result,
        "trace": tracer.format_trace()
    } == snapshot
```

## Key Benefits
1. **No Manual Test Data**: Capture real arguments automatically
2. **Complete Coverage**: Trace entire execution flows, not just outputs
3. **Production Safe**: Security filtering and minimal overhead
4. **Legacy Friendly**: Works with existing untestable code
5. **Syrupy Integration**: Leverages modern snapshot testing

## Common Patterns
- Use capture for replay testing with real data
- Use tracing for validating complex workflows
- Combine both for comprehensive test coverage
- Apply security filtering in production environments

See `workflows/` for detailed development patterns.