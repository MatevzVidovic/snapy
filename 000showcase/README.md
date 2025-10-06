# Snapy Showcase

A simple demonstration of Snapy's core functionality with various data structures.

## What's included

- **data_structures.py**: Functions that work with complex data types
- **test_showcase.py**: Tests using captured arguments and function tracing
- **captures/**: Directory where captured arguments are stored

## Data structures tested

- Custom classes (`Person`)
- Dataclasses (`Product`)
- Linked lists (`ListNode`)
- Complex nested dictionaries
- Numpy arrays (if numpy available)
- Pandas DataFrames (if pandas available)

## Quick start

1. **Generate captures**:
   ```bash
   cd 000showcase
   PYTHONPATH=../src python data_structures.py
   ```

2. **Run tests with captured data**:
   ```bash
   PYTHONPATH=../src python -m pytest test_showcase.py -v
   ```

## Core Snapy features demonstrated

- `@capture_args()` decorator for automatic argument capture
- `load_capture()` for replaying captured arguments in tests
- `FunctionTracer` for tracing function execution
- Snapshot testing integration with syrupy

This showcase focuses on the most essential Snapy functionality that users will actually use in their projects.

## Test Results

✅ **Works perfectly with pickle**:
- Custom classes (Person)
- Dataclasses (Product)
- Complex nested dictionaries
- Standard Python types

⚠️ **Minor limitation found**:
- Custom classes defined in different modules can have pickle serialization issues
- See `dill_plan.md` for solution using dill as alternative serializer

## Testing the showcase

```bash
# Run the data generator
PYTHONPATH=../src python3 data_structures.py

# Run the tests
PYTHONPATH=../src python3 simple_test_fixed.py
```

## Key takeaway

Snapy works excellently with almost all data structures. The one limitation (cross-module custom classes) has been solved by integrating dill as the default serialization backend.

## Dill Integration (NEW!)

Snapy now uses **dill** by default instead of pickle, which provides:
- ✅ Better serialization of custom classes across modules
- ✅ Support for lambda functions and nested classes
- ✅ Handles objects from `__main__` module
- ✅ Better error messages and debugging
- ✅ Backward compatibility with existing pickle files

### Configuration Options

Set via environment variables or `.env` file:
```bash
# Choose serialization backend
SNAP_CAPTURE_SERIALIZATION_BACKEND=dill    # recommended (default)
SNAP_CAPTURE_SERIALIZATION_BACKEND=pickle  # legacy compatibility
SNAP_CAPTURE_SERIALIZATION_BACKEND=auto    # auto-detect best available

# Enable fallback from pickle to dill if needed
SNAP_CAPTURE_FALLBACK_TO_DILL=true  # default
```

With dill integration, the ListNode serialization issue is completely resolved!