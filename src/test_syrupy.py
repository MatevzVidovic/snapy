
import os
from pathlib import Path
import examples.basics as b

from unittest.mock import Mock
from pytest_mock import MockerFixture, MockType


def test_greeting():
    b.main()

# tests/test_greeting.py
def test_do_ops(snapshot):

    returned = b.do_ops(b.RealOpsOne(), 1, 2)
    assert returned == snapshot


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
# def test_real_ops_one_concatenation(snapshot):

#     table = cch().load_all(b.RealOpsOne.concatenation)
#     print(f"table: {table}")

#     for _, entry in table.items():
#         result = b.RealOpsOne().concatenation(*entry["args"], **entry["kwargs"])
#         assert result == snapshot

def test_real_ops_one_plus(snapshot):

    table = cch.load_all(b.RealOpsOne.plus)
    print(f"table: {table}")

    for _, entry in table.items():
        # print(b.RealOpsOne().plus(5, 8))
        result = b.RealOpsOne().plus(*entry["args"][1:], **entry["kwargs"])
        # print(f"result: {result}")
        assert result == snapshot





def test_do_ops_DI_with_protocol_mock_snap(mocker: MockerFixture, snapshot):

    """

    - v plus_mock imamo potem fn plus_wrapper ki ima v sebi potem plus().
    
    In če je plus_wrapper že imel take argumente (vidimo v capture load) potem samo returnamo to.

    Če še ni imel, poženemo plus wrapper (na njim je @capture torej se bo zdaj shranilo).

    - V testu imamo pogledamo za dotenv spremenljivko .
    Če je ta false ali none, in ne najdemo matching signaturea v loaded captures, damo Exception.
    """

    table_tests = cch.load_all(b.do_ops)
    for test_case, captures in table_tests.items():
        ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)

        def plus_mock(*args, **kwargs):
            import src.capture.capture as c
            side_effect_target_path = c.side_effect_target_path(test_do_ops_DI_with_protocol_mock_snap, plus_mock, test_case)
            returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path)
            if was_found:
                return returned
            
            @c.capture(max_captures=float("inf"), target_path=side_effect_target_path)
            def plus_wrapper(*args, **kwargs):
                import examples.basics as b
                return b.RealOpsOne.plus(*args, **kwargs)
            return plus_wrapper(*args, **kwargs)


        def expression_mock(*args, **kwargs):
            import src.capture.capture as c
            side_effect_target_path = c.side_effect_target_path(test_do_ops_DI_with_protocol_mock_snap, expression_mock, test_case)
            returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path)
            if was_found:
                return returned
            
            @c.capture(max_captures=float("inf"), target_path=side_effect_target_path)
            def expression_wrapper(*args, **kwargs):
                import examples.basics as b
                return b.RealOpsOne.expression(*args, **kwargs)
            return expression_wrapper(*args, **kwargs)
        

        def concatenation_mock(*args, **kwargs):
            import src.capture.capture as c
            side_effect_target_path = c.side_effect_target_path(test_do_ops_DI_with_protocol_mock_snap, concatenation_mock, test_case)
            returned, was_found = c.side_effect_lookup(args, kwargs, side_effect_target_path)
            if was_found:
                return returned
            
            @c.capture(max_captures=float("inf"), target_path=side_effect_target_path)
            def concatenation_wrapper(*args, **kwargs):
                import examples.basics as b
                return b.RealOpsOne.concatenation(*args, **kwargs)
            return concatenation_wrapper(*args, **kwargs)


    

        ops.plus.side_effect = plus_mock
        ops.expression.side_effect = expression_mock
        ops.concatenation.side_effect = concatenation_mock

        print_spy = mocker.patch("examples.basics.print")

        returned = b.do_ops_DI(*captures["args"], **captures["kwargs"])

        c.assert_side_effect_calls(test_do_ops_DI_with_protocol_mock_snap, concatenation_mock, test_case, ops.plus)
        c.assert_side_effect_calls(test_do_ops_DI_with_protocol_mock_snap, expression_mock, test_case, ops.expression)
        c.assert_side_effect_calls(test_do_ops_DI_with_protocol_mock_snap, concatenation_mock, test_case, ops.concatenation)

        assert [returned] + [call.args for call in print_spy.call_args_list] == snapshot
        
        