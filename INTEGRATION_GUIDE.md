# PySnap Integration Guide

**Enhanced Snapshot Testing with Function Tracing**

PySnap extends traditional snapshot testing by capturing complete function call trees, including arguments, return values, and nested function calls. This guide shows how to integrate PySnap into existing large projects.

## Features

✅ **Function Arguments & Return Values**: Capture all inputs and outputs  
✅ **Nested Function Calls**: Trace inner functions and their interactions  
✅ **Multiple Integration Methods**: Decorators, context managers, or testing utilities  
✅ **Zero Code Modification**: Use context managers for non-invasive tracing  
✅ **Syrupy Compatible**: Drop-in replacement for existing snapshot tests  
✅ **Production Safe**: Conditional enablement and filtering capabilities

## Quick Start

### Installation

```bash
# Add PySnap to your project
pip install -e /path/to/pysnap

# Or add to requirements.txt / pyproject.toml
# pysnap @ file:///path/to/pysnap
```

### Basic Usage

```python
from pysnap import trace_calls, TracedSnapshot

# Option 1: Context Manager (Zero modification)
with trace_calls() as tracer:
    result = my_function("arg1", "arg2")

print(tracer.get_formatted_trace())
# Output:
# ├─ Function: my_function(arg1='arg1', arg2='arg2')
#   ├─ Function: helper_function(data='arg1')
#   │  └─ Returns: 'processed_arg1'
#   └─ Returns: 'final_result'

# Option 2: Snapshot Testing
def test_my_function(snapshot):
    from pysnap import TracedSnapshot
    
    traced = TracedSnapshot()
    result = traced.capture_trace(my_function, "test", "data")
    
    # Creates snapshot of complete call tree
    traced.assert_match(snapshot)
```

## Integration Approaches

### 1. Testing Integration (Recommended for existing projects)

**Best for**: Existing test suites, CI/CD integration, debugging

```python
# tests/test_with_pysnap.py
from pysnap import TracedSnapshot, trace_calls
from myproject.module import complex_function

def test_complex_workflow(snapshot):
    """Test with complete call tree capture."""
    traced = TracedSnapshot()
    result = traced.capture_trace(complex_function, input_data)
    
    # Snapshot includes:
    # - Function arguments
    # - All nested calls  
    # - Return values
    # - Call depth/structure
    traced.assert_match(snapshot)

def test_multiple_scenarios():
    """Test multiple scenarios in one trace."""
    with trace_calls(filter_modules=["myproject"]) as tracer:
        scenario1 = function_a("data1")
        scenario2 = function_b("data2") 
        scenario3 = function_c("data3")
    
    # Analyze complete execution flow
    trace = tracer.get_formatted_trace()
    assert "function_a" in trace
    assert "function_b" in trace
    assert "function_c" in trace
```

### 2. Decorator Integration

**Best for**: Specific functions you want to always trace

```python
from pysnap import trace_snapshot

@trace_snapshot()
def critical_business_function(data, config):
    """Function that needs comprehensive tracing."""
    step1 = preprocess(data)
    step2 = apply_rules(step1, config)
    return finalize(step2)

# Usage
result = critical_business_function(my_data, my_config)

# Access trace data
print(critical_business_function.get_last_formatted())
```

### 3. Context Manager Integration

**Best for**: Debugging, development, conditional tracing

```python
from pysnap import trace_calls
import os

# Conditional tracing in production
if os.getenv('ENABLE_TRACING'):
    with trace_calls(filter_modules=["myproject"]) as tracer:
        result = complex_operation()
        
    # Log trace for debugging
    logger.debug(f"Execution trace: {tracer.get_formatted_trace()}")
else:
    result = complex_operation()
```

## Advanced Integration Patterns

### Module-Level Filtering

```python
# Only trace your application code, ignore libraries
with trace_calls(filter_modules=["myproject", "myapp"]) as tracer:
    result = function_that_uses_many_libraries()

# Trace shows only myproject/myapp functions
```

### Custom Snapshot Formatting

```python
class CustomTracedSnapshot(TracedSnapshot):
    def custom_format(self):
        """Custom formatting for your project needs."""
        trace = self.get_trace()
        
        # Group by modules
        modules = {}
        for event in trace:
            module = event.filename.split('/')[-1]
            if module not in modules:
                modules[module] = []
            modules[module].append(event)
        
        return self._format_by_modules(modules)
```

### Performance-Aware Integration

```python
from pysnap import trace_calls
import time

class PerformanceTracer:
    def __init__(self, filter_modules=None):
        self.filter_modules = filter_modules
        
    def trace_with_timing(self, func, *args, **kwargs):
        start_time = time.time()
        
        with trace_calls(filter_modules=self.filter_modules) as tracer:
            result = func(*args, **kwargs)
            
        end_time = time.time()
        
        return {
            'result': result,
            'trace': tracer.get_formatted_trace(),
            'execution_time': end_time - start_time,
            'function_calls': len(tracer.get_trace())
        }

# Usage
perf_tracer = PerformanceTracer(filter_modules=["myproject"])
analysis = perf_tracer.trace_with_timing(expensive_function, data)

print(f"Execution time: {analysis['execution_time']:.2f}s")
print(f"Function calls: {analysis['function_calls']}")
print(f"Trace:\n{analysis['trace']}")
```

## Large Project Integration Strategies

### 1. Gradual Rollout

```python
# Phase 1: Add to critical tests only
def test_payment_processing(snapshot):
    with trace_calls(filter_modules=["payments"]) as tracer:
        result = process_payment(test_payment_data)
    traced_snapshot = TracedSnapshot()
    traced_snapshot.tracer = tracer.tracer
    traced_snapshot.assert_match(snapshot)

# Phase 2: Add to all integration tests
# Phase 3: Add to specific modules
# Phase 4: Optional production debugging
```

### 2. Team-Specific Integration

```python
# For Backend Teams
from pysnap import trace_calls

def trace_api_endpoint(filter_business_logic=True):
    modules = ["business_logic", "data_access"] if filter_business_logic else None
    return trace_calls(filter_modules=modules)

# For Frontend Teams  
def trace_component_lifecycle(component_name):
    return trace_calls(filter_modules=[f"components.{component_name}"])

# For Data Teams
def trace_data_pipeline(pipeline_name):
    return trace_calls(filter_modules=[f"pipelines.{pipeline_name}"])
```

### 3. CI/CD Integration

```python
# conftest.py (pytest configuration)
import os
from pysnap import TracedSnapshot

def pytest_configure(config):
    """Enable enhanced tracing in CI/CD."""
    if os.getenv('CI') or config.getoption('--trace-functions'):
        config.enable_function_tracing = True

@pytest.fixture
def traced_snapshot(request):
    """Enhanced snapshot fixture for CI/CD."""
    if hasattr(request.config, 'enable_function_tracing'):
        return TracedSnapshot()
    else:
        return None  # Fall back to regular snapshot
```

### 4. Production Debugging Integration

```python
import logging
from pysnap import trace_calls

class ProductionDebugger:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        
    def debug_request(self, request_id, func, *args, **kwargs):
        """Debug specific requests in production."""
        if self._should_trace(request_id):
            with trace_calls(filter_modules=["myapp"]) as tracer:
                result = func(*args, **kwargs)
                
            self.logger.info(
                f"Request {request_id} trace: {tracer.get_formatted_trace()}"
            )
            return result
        else:
            return func(*args, **kwargs)
    
    def _should_trace(self, request_id):
        # Implement your tracing logic
        # e.g., sample percentage, specific user IDs, etc.
        return request_id.endswith('debug')

# Usage in production
debugger = ProductionDebugger()

def api_handler(request):
    return debugger.debug_request(
        request.id, 
        process_api_request, 
        request
    )
```

## Migration from Existing Snapshot Tests

### Syrupy Migration

```python
# Before (standard syrupy)
def test_function(snapshot):
    result = my_function("input")
    assert snapshot == result

# After (enhanced with PySnap)
def test_function(snapshot):
    from pysnap import TracedSnapshot
    
    traced = TracedSnapshot()
    result = traced.capture_trace(my_function, "input")
    
    # Now captures complete call tree instead of just result
    traced.assert_match(snapshot)
```

### Custom Snapshot Migration

```python
# Before (custom snapshot implementation)
def test_function():
    result = my_function("input")
    expected = load_expected_result()
    assert result == expected

# After (enhanced tracing)
def test_function(snapshot):
    from pysnap import trace_calls
    
    with trace_calls() as tracer:
        result = my_function("input")
    
    # Captures both result AND execution path
    execution_data = {
        'result': result,
        'trace': tracer.get_formatted_trace()
    }
    
    assert snapshot == execution_data
```

## Best Practices

### 1. Module Filtering

```python
# ✅ Good: Filter to your application modules
with trace_calls(filter_modules=["myapp", "myproject"]):
    result = function()

# ❌ Avoid: Tracing everything (noisy and slow)
with trace_calls():
    result = function()
```

### 2. Conditional Enablement

```python
# ✅ Good: Conditional tracing
import os

ENABLE_TRACING = os.getenv('DEBUG_TRACING', False)

if ENABLE_TRACING:
    with trace_calls(filter_modules=["myapp"]) as tracer:
        result = function()
    print(tracer.get_formatted_trace())
else:
    result = function()
```

### 3. Test Organization

```python
# ✅ Good: Separate traced tests
def test_function_behavior():
    """Test basic functionality."""
    result = my_function("input")
    assert result == expected

def test_function_execution_trace(snapshot):
    """Test complete execution flow."""
    traced = TracedSnapshot()
    result = traced.capture_trace(my_function, "input")
    traced.assert_match(snapshot)
```

## Performance Considerations

- **Module Filtering**: Always filter to relevant modules to reduce overhead
- **Conditional Enablement**: Use environment variables for production
- **Test Separation**: Keep traced tests separate from performance tests
- **Selective Tracing**: Only trace critical paths in production

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PySnap is in your Python path
2. **No Traces Captured**: Check module filtering settings
3. **Too Many Traces**: Add more specific module filters
4. **Performance Impact**: Use conditional enablement

### Debug Mode

```python
# Enable debug output
import logging
logging.basicConfig(level=logging.DEBUG)

from pysnap import trace_calls

with trace_calls(filter_modules=["myapp"]) as tracer:
    result = function()
    print(f"Captured {len(tracer.get_trace())} events")
```

## Example Projects

See the `examples/` directory for complete integration examples:

- **Django Integration**: Web framework tracing
- **FastAPI Integration**: API endpoint tracing  
- **Data Pipeline Integration**: ETL process tracing
- **Microservice Integration**: Service-to-service call tracing

## Support

For integration questions or issues:

1. Check the troubleshooting section above
2. Review example projects
3. Create an issue with integration details

---

**PySnap** - Enhanced snapshot testing for comprehensive function tracing.