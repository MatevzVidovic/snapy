# Snapy Features

## Setup
- using poetry and conda

## Basic snap testing - already done by syrupy
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


# Side-effect Dependency Injection capture system

- When making a unit test or snap test, it is annoying to set up mock fns for subfns (the fns that the tested fn uses inside of it).
- We can use special argument capture from inside the unit test:
Go see test_syrupy.py::test_do_ops_DI_with_protocol_mock_snap() for an example of how to do this.

Example:
```python


def test_do_ops_DI_with_protocol_mock_snap(mocker: MockerFixture, snapshot):
    
    ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)


    test_specifier = (test_do_ops_DI_with_protocol_mock_snap, test_case)
    # Create fn_mock - this will be the mock method in the DI mock object.
    def plus_mock(*args, **kwargs):
        import src.capture.capture as c
        # get unique storage path for this (test_fn + test case + fn_mock)
        side_effect_target_path = c.side_effect_target_path(*test_specifier, plus_mock)
        # if fn_mock has been previously called with this args/kwargs, return stored result
        # if env var SIDE_EFFECT_TEST_MODE=1 and no match found, error is raised
        returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path, in_test_mode=os.getenv("SIDE_EFFECT_TEST_MODE") == "1")
        if was_found:
            return returned
        
        # main idea: if no match found, call real fn and store what it returns.
        # how: To achieve this, we wrap the real call fn, so that we can add a capture decorator to it.
        # Notice that target_path is for the plus_mock fn, not for plus_wrapper.
        # This is done so that we can use assert_side_effect_calls() later on (plus_wrapper is an inner fn and can't be accessed outside).
        # And functionally it makes no diference, since the args/kwargs are the same for plus_mock and plus_wrapper.
        @c.capture(max_captures=float("inf"), target_path=side_effect_target_path)
        def plus_wrapper(*args, **kwargs):
            import examples.basics as b
            return b.RealOpsOne().plus(*args, **kwargs)
        return plus_wrapper(*args, **kwargs)


    
    ops.plus.side_effect = plus_mock

```