# PySnap Context Documentation

Concise documentation for quick Claude Code onboarding to the PySnap project.

## Project Overview
PySnap is a Python testing framework with two main components:
- **snapy_capture**: Automatic function argument capture for replay testing
- **snapy_testing**: Function tracing with sys.settrace + syrupy integration

## Quick Navigation

### Essential Files
- `quick-start/` - Immediate project understanding and common tasks
- `architecture/` - Core system design and patterns
- `modules/` - Brief module summaries and key APIs
- `workflows/` - Common development and testing workflows

### Key Commands
```bash
# Testing
python3 -m pytest
PYTHONPATH=src python3 -m pytest

# Examples
cd src/snapy_capture/examples && python3 basic_usage.py
PYTHONPATH=. python3 enhanced_snap_test.py
```

### Project Structure
```
src/
├── snapy_capture/     # Argument capture framework
├── snapy_testing/     # Function tracing framework
└── __snapshots__/     # Syrupy snapshot files
```

This documentation provides minimal but sufficient context for productive Claude Code sessions.