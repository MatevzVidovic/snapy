# PySnap Project Structure Improvement Plan

## Current Issues Identified

1. **Inconsistent naming**: `snap_capture` vs `snapy_capture` directories both exist
2. **Cluttered src root**: Example files mixed with core modules (basicExample.py, enhanced_example.py in src/)
3. **Scattered documentation**: Docs in module directories (docs.md, setup.md in snapy_testing/)
4. **Multiple __pycache__ directories**: 8 scattered throughout
5. **Clutter directory**: Contains various old files and duplicates (keeping as-is)
6. **Inconsistent test organization**: Some tests inside modules, unclear test vs example separation

## Proposed Restructure

```
snapy/
├── pyproject.toml
├── .env.example
├── README.md (create from CLAUDE.md)
├── CLAUDE.md
│
├── src/
│   └── snapy/            # Single unified package name
│       ├── __init__.py
│       ├── capture/      # Renamed from snapy_capture
│       │   ├── __init__.py
│       │   ├── capture.py
│       │   ├── storage.py
│       │   ├── config.py
│       │   ├── filters.py
│       │   └── loader.py
│       └── testing/      # Renamed from snapy_testing
│           ├── __init__.py
│           ├── tracer.py
│           ├── snapshot.py
│           └── advanced/
│
├── tests/                # All tests in one place
│   ├── unit/
│   │   ├── capture/
│   │   │   ├── test_capture.py
│   │   │   ├── test_storage.py
│   │   │   ├── test_config.py
│   │   │   └── test_loader.py
│   │   └── testing/
│   │       ├── test_tracer.py
│   │       └── test_snapshot.py
│   └── integration/
│       ├── test_integration.py
│       └── test_workflows.py
│
├── examples/             # All examples in one place
│   ├── basic/
│   │   ├── capture_basics.py
│   │   └── tracing_basics.py
│   ├── advanced/
│   │   ├── production_capture.py
│   │   ├── complex_tracing.py
│   │   └── integration_example.py
│   └── legacy/
│       └── legacy_integration.py
│
├── docs/                # Consolidated documentation
│   ├── user/           # From my_docs
│   ├── api/            # From llm_docs
│   ├── quickstart/     # From context_docs
│   └── quiz/           # Quiz questions
│
├── data/               # Runtime data
│   ├── captures/       # Default capture storage
│   └── snapshots/      # Syrupy snapshots
│
└── .clutter/           # Keep existing old/deprecated files as-is
```

## Key Changes

1. **Unified package name**: `snapy` with submodules `capture` and `testing`
2. **Clear separation**: src/ for source, tests/ for tests, examples/ for examples
3. **Single documentation root**: docs/ with clear subdirectories
4. **Clean src directory**: No example files or test files mixed with source
5. **Consistent module naming**: `capture` and `testing` (shorter, clearer)
6. **Remove duplication**: Delete `snap_capture` directory (appears to be duplicate)
7. **Keep .clutter as-is**: No need to move old files
8. **Gitignore __pycache__**: Add proper .gitignore to exclude all __pycache__ directories

## Migration Impact

### ⚠️ BREAKING CHANGES
This restructure will break all existing import statements. Users will need to update:

**Before:**
```python
from snapy_capture import capture_args
from snapy_testing import FunctionTracer
```

**After:**
```python
from snapy.capture import capture_args
from snapy.testing import FunctionTracer
```

### Migration Steps

1. Create new directory structure
2. Move and rename modules (snapy_capture → snapy/capture)
3. **Update all imports in source files** (CRITICAL STEP)
4. Move tests to centralized tests/ directory
5. Move examples to examples/ directory
6. Consolidate documentation to docs/
7. Update pyproject.toml with new package structure
8. Clean up __pycache__ and add to .gitignore
9. Update CLAUDE.md with new structure

## Benefits

This restructure will make the project:
- More intuitive for new developers
- Easier to navigate and understand
- Consistent with Python packaging best practices
- Cleaner with proper separation of concerns
- Better organized for maintenance and growth

## Recommendations

1. **Version this as a major release** (e.g., 2.0.0) due to breaking changes
2. **Provide migration guide** for existing users
3. **Consider deprecation period** with backwards compatibility shims
4. **Update all documentation** to reflect new import paths