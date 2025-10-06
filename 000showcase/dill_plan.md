# Dill Integration Plan for Snapy

## Identified Serialization Issues

During testing of the Snapy showcase, we discovered a specific limitation with pickle serialization:

### Issue: Custom Class Module Resolution
- **Problem**: `ListNode` class fails to deserialize with error: "Can't get attribute 'ListNode' on module '__main__'"
- **Cause**: When a custom class is pickled from one module and unpickled from another, pickle can't resolve the class reference
- **Current Status**: 3/4 test cases work perfectly, only custom classes defined in different modules fail

### Successful Serialization Cases
- ✅ **Person class**: Works (defined in data_structures.py, loaded from data_structures.py)
- ✅ **Product dataclass**: Works perfectly
- ✅ **Complex nested dictionaries**: No issues
- ✅ **Lists and standard Python types**: Perfect
- ❌ **ListNode class**: Fails due to module resolution

## Why Dill Would Solve This

Dill extends pickle with several advantages:
1. **Better module handling**: Can serialize objects from `__main__` and handle module path changes
2. **Enhanced class support**: Handles dynamically created classes and nested classes
3. **Function serialization**: Can serialize lambda functions and local functions
4. **Backward compatibility**: Drop-in replacement for pickle in most cases

## Implementation Plan

### Phase 1: Add Dill as Optional Dependency

```python
# In pyproject.toml
[project.optional-dependencies]
enhanced_serialization = ["dill>=0.3.6"]
```

### Phase 2: Create Configurable Storage Backend

```python
# In src/snapy/capture/config.py
class CaptureConfig:
    # Add new configuration options
    serialization_backend: str = "pickle"  # "pickle" or "dill"
    fallback_to_dill: bool = True  # Auto-fallback if pickle fails
```

### Phase 3: Modify Storage Layer

```python
# In src/snapy/capture/storage.py
class CaptureStorage:
    def __init__(self, base_path: str, backend: str = "auto"):
        self.backend = backend
        self._setup_serializer()

    def _setup_serializer(self):
        if self.backend == "dill" or (self.backend == "auto" and self._has_dill()):
            import dill
            self.serializer = dill
        else:
            import pickle
            self.serializer = pickle

    def _has_dill(self) -> bool:
        try:
            import dill
            return True
        except ImportError:
            return False

    def save_capture(self, ...):
        try:
            # Try with configured serializer
            with open(filepath, 'wb') as f:
                self.serializer.dump(captured_call, f)
        except Exception as e:
            if self.backend == "auto" and self.serializer.__name__ == "pickle":
                # Fallback to dill if available
                if self._has_dill():
                    import dill
                    with open(filepath, 'wb') as f:
                        dill.dump(captured_call, f)
                else:
                    raise e
            else:
                raise e
```

### Phase 4: Update Configuration

```python
# Environment variable support
SNAP_CAPTURE_SERIALIZATION_BACKEND=dill  # or pickle, auto
SNAP_CAPTURE_FALLBACK_TO_DILL=true
```

### Phase 5: Testing and Validation

1. **Compatibility Test**: Ensure dill-serialized captures can be read by pickle (when possible)
2. **Performance Test**: Compare serialization speed and file sizes
3. **Edge Case Test**: Test complex cases like lambdas, nested functions
4. **Fallback Test**: Verify graceful degradation when dill unavailable

## Migration Strategy

### For Existing Users
- **Default behavior**: Keep using pickle to maintain compatibility
- **Opt-in enhancement**: Users can enable dill via config
- **Automatic fallback**: If pickle fails and dill available, auto-retry with dill

### For New Projects
- **Recommended setup**: Include dill in optional dependencies
- **Auto-detection**: Use "auto" backend to get best available serializer

## Benefits After Implementation

1. **Solve ListNode issue**: Custom classes will serialize/deserialize correctly
2. **Enhanced capabilities**: Support for lambda functions, local classes
3. **Better debugging**: Dill provides better error messages for serialization failures
4. **Future-proof**: Handle more complex data structures as they arise

## Minimal Implementation (Quick Win)

For immediate resolution of the showcase issue, add this to storage.py:

```python
def _safe_serialize(self, obj, filepath):
    """Try pickle first, fallback to dill if available."""
    try:
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(obj, f)
    except Exception as e:
        try:
            import dill
            with open(filepath, 'wb') as f:
                dill.dump(obj, f)
            print(f"Note: Used dill serialization for {filepath}")
        except ImportError:
            raise e  # Original pickle error if dill unavailable
        except Exception:
            raise e  # Original pickle error if dill also fails
```

This would immediately fix the ListNode serialization issue while maintaining backward compatibility.

## Estimated Impact

- **Development time**: 2-3 days for full implementation
- **Risk level**: Low (dill is mature and widely used)
- **User impact**: Positive - more reliable serialization with minimal changes
- **Performance impact**: Negligible for most use cases