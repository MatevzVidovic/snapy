# Snapy Features

## Setup
- using poetry and conda

## Basic snap testing
- do unit-test-like definition of input args to the fn
- run the fn with these args
- capture the output. Compare it to previous output.

## Argument Capture System

### Idea
- capture arguments to fns while running the project in a production-like yet simplified setting
- capture returns of function as well
- this way, we don't need to make up arguments in unit and snap testing

### Point

• Automatic function argument capture in via `@capture_args()` decorator while running in production
• Enables capture replay for snap testing
• Using dill for serialization and loading these objects in snap tests (use them as inputs to the fn)
• Retain 2 input tuples for this fn. If 2 already exist, do not capture args.

