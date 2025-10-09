# Snapy Features

## Setup
- using poetry and conda

## Basic snap testing
- do unit-test-like definition of input args to the fn
- run the fn with these args
- capture the output. Compare it to previous output.
- We can use Syrupy for this.

## Argument Capture System

### Idea
- capture arguments to fns while running the project in a production-like yet simplified setting
- capture returns of function as well
- this way, we don't need to make up arguments in unit and snap testing

### Point

- Automatic function argument capture in via `@capture_args()` decorator while running in production
- Enables capture replay for snap testing
- Using dill for serialization and loading these objects in snap tests (use them as inputs to the fn)
- Retain 2 past (args, returned) values. If 2 already exist, do not do capture anymore.


# Mock dependency capture

- When making a unit test or snap test, it is annoying to set up mock fns for subfns (the fns that the tested fn uses inside of it).
- We can use special argument capture from inside the unit test:
CAPTURE_MODE = True
def mock_subfn(*args, **kwargs):
    
    global CAPTURE_MODE
    is_already_captured, captured_return = load_mock_capture("mock_subfn", *args **kwargs)
    if is_already_captured:
        return captured_return
    
    if CAPTURE_MODE:
        retured = subfn(*args **kwargs)
        create_mock_capture(returned, "mock_subfn", *args **kwargs)
        return returned
    else:
        save_mismatched_capture("mock_subfn", *args **kwargs) # easier to check what went wrong
        raise Exception ArgumentsNotCaptured
