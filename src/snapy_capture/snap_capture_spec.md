# Snap Capture Decorator Specification

## Core Functionality
Decorator that captures function input arguments (using pickle or faster equivalent) to replay function calls in snap tests without manually creating arguments.

## Configuration
- **Path**: Configurable storage path (default: `./snap_capture`)
- **Retention**: Keep last N captures (default: 2)
- **Overwrite**: Only save new captures when none exist (unless `overwrite=True`)
- **Name filtering**: Ignore args with specific names, and ignore specific dictionary keys in certain of these args

## Snap test example
- Easily load the necessary args for the test function

## Control Mechanisms
- **.env file**: Specifies which modules/functions to ignore
- **Global toggle**: Environment variable to enable/disable all capturing

## Production Optimization - advice for the user
- Keep captured objects minimal when running in production environment.
- Ignore large args (like ML models) if that becomes a problem.
Either make a basic version with preset weights in the snap test on the fly,
or capture them once in some place, wherever, and then load that specific one in your snap test