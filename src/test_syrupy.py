
import examples.basics as b


def test_greeting():
    b.main()

# tests/test_greeting.py
def test_do_ops(snapshot):

    returned = b.do_ops(b.RealOpsOne(), 1, 2)
    assert returned == snapshot


def test_do_ops_with_protocol_mock(mocker, snapshot):
    ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)
    ops.plus.return_value = 3
    # THIS IS CELARLY PROBLEMATIC.
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
# def test_real_ops_one_concatenation(snapshot):

#     table = c.CaptureHandler().load_all(b.RealOpsOne.concatenation)
#     print(f"table: {table}")

#     for _, entry in table.items():
#         result = b.RealOpsOne().concatenation(*entry["args"], **entry["kwargs"])
#         assert result == snapshot

def test_real_ops_one_plus(snapshot):

    table = c.CaptureHandler().load_all(b.RealOpsOne.plus)
    print(f"table: {table}")

    for _, entry in table.items():
        # print(b.RealOpsOne().plus(5, 8))
        result = b.RealOpsOne().plus(*entry["args"][1:], **entry["kwargs"])
        # print(f"result: {result}")
        assert result == snapshot