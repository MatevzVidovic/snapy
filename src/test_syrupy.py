
import os
from pathlib import Path
import examples.basics as b

from unittest.mock import Mock
from pytest_mock import MockerFixture, MockType


# ---------- Basic snapshot testing ----------

def test_do_ops(snapshot):

    returned = b.do_ops(b.RealOpsOne(), 1, 2)
    assert returned == snapshot



# ---------- Example of bad Dependency Injection (DI) snapshot testing ----------

def test_do_ops_with_protocol_mock(mocker, snapshot):
    ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)
    ops.plus.return_value = 3
    # THIS IS CLARLY PROBLEMATIC.
    # The 2 lines below are wrong - that is not at is returned.
    # But since it is never used as an input, 
    # we dont even know that that is what is returned.
    ops.expression.return_value = "expr(1, 2)"
    ops.concatenation.return_value = "concat(1, 2)"

    print_spy = mocker.patch("examples.basics.print")

    b.do_ops(ops, 1, 2)

    ops.plus.assert_called_once_with(1, 2, c=8)
    ops.expression.assert_called_once_with(1, 2)
    ops.concatenation.assert_called_once_with(1, 2)
    assert [call.args for call in print_spy.call_args_list] == snapshot



# ---------- Example of good pass-through Dependency Injection (DI) snapshot testing ----------

def test_do_ops_DI_with_protocol_mock(mocker, snapshot):

    real_ops = b.RealOpsOne()

    ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)
    ops.plus.return_value = 3
    ops.expression.side_effect = real_ops.expression
    ops.concatenation.side_effect = real_ops.concatenation

    # print_spy = mocker.patch(real_ops, "concatenation", wraps=real_ops.concatenation)
    # print_spy = mocker.patch("examples.basics.RealOpsOne.concatenation")
    # print_spy = mocker.patch(real_ops, "concatenation")
    print_spy = mocker.patch("examples.basics.RealOpsOne.concatenation", wraps=real_ops.concatenation)


    # print_spy = mocker.patch("examples.basics.print")

    returned = b.do_ops_DI(ops, 1, 2)

    print(f"\nspied: {print_spy.call_args_list}")

    ops.plus.assert_called_once_with(1, 2)
    ops.expression.assert_called_once()
    ops.concatenation.assert_called()

    # assert [call.args for call in print_spy.call_args_list] == snapshot

    assert returned == snapshot







import src.capture.capture as c
cch = c.CaptureHandler

# ---------- Argument capture snap testing example ----------

def test_real_ops_one_plus(snapshot):

    table_tests = cch.get_blob_paths(cch.get_target_path(b.RealOpsOne.plus))

    for blob_path in table_tests:
        captures = cch.get_blob(blob_path)
        result = b.RealOpsOne().plus(*captures["args"][1:], **captures["kwargs"])
        assert result == snapshot




# ---------- Side-effect capture DI snap testing example ----------

def test_do_ops_DI_with_protocol_mock_snap(mocker: MockerFixture, snapshot):


    print(f"os.getenv('SNAPY_CAPTURE_ENABLED')): {os.getenv('SNAPY_CAPTURE_ENABLED')}")
    print(f"os.getenv('SIDE_EFFECT_TEST_MODE')): {os.getenv('SIDE_EFFECT_TEST_MODE')}")


    table_tests = cch.get_blob_paths(cch.get_target_path(b.do_ops_DI))
    if len(table_tests) == 0:
        raise ValueError("No captures found for do_ops_DI - first run your production with SNAPY_CAPTURE_ENABLED=1")
    
    for blob_path in table_tests:
        test_case = blob_path.name
        captures = cch.get_blob(blob_path)
        ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)



        # ---------- Idiomatic use of side-effect capture ----------

        test_specifier = (test_do_ops_DI_with_protocol_mock_snap, test_case)
        # Create fn_mock - this will be the mock method in the DI mock object.
        def plus_mock(*args, **kwargs):
            import src.capture.capture as c
            # get unique storage path for this (test_fn + test case + fn_mock)
            side_effect_target_path = c.side_effect_target_path(*test_specifier, plus_mock)
            # if fn_mock has been previously called with this args/kwargs, return stored result
            # if env var SIDE_EFFECT_TEST_MODE=1 and no match found, error is raised
            returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path)
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





        def expression_mock(*args, **kwargs):
            import src.capture.capture as c
            side_effect_target_path = c.side_effect_target_path(*test_specifier, expression_mock)
            returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path)
            if was_found:
                return returned
            
            @c.capture(max_captures=float("inf"), target_path=side_effect_target_path)
            def expression_wrapper(*args, **kwargs):
                import examples.basics as b
                return b.RealOpsOne().expression(*args, **kwargs)
            return expression_wrapper(*args, **kwargs)
        

        def concatenation_mock(*args, **kwargs):
            import src.capture.capture as c
            side_effect_target_path = c.side_effect_target_path(*test_specifier, concatenation_mock)
            returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path)
            if was_found:
                return returned
            
            @c.capture(max_captures=float("inf"), target_path=side_effect_target_path)
            def concatenation_wrapper(*args, **kwargs):
                import examples.basics as b
                return b.RealOpsOne().concatenation(*args, **kwargs)
            return concatenation_wrapper(*args, **kwargs)


    

        ops.plus.side_effect = plus_mock
        ops.expression.side_effect = expression_mock
        ops.concatenation.side_effect = concatenation_mock

        print_spy = mocker.patch("examples.basics.print")

        returned = b.do_ops_DI(ops, *captures["args"][1:], **captures["kwargs"])

        c.assert_side_effect_calls(*test_specifier, plus_mock, ops.plus)
        c.assert_side_effect_calls(*test_specifier, expression_mock, ops.expression)
        c.assert_side_effect_calls(*test_specifier, concatenation_mock, ops.concatenation)

        assert [returned] + [call.args for call in print_spy.call_args_list] == snapshot
        
        