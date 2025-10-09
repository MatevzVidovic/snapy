
import examples.basics as b

# tests/test_greeting.py
def test_do_ops(snapshot):

    returned = b.do_ops(b.RealOpsOne(), 1, 2)
    assert returned == snapshot


def test_do_ops_with_protocol_mock(mocker, snapshot):
    ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)
    ops.plus.return_value = 3
    # THIS IS CELARLY PROBLEMATIC.
    # The 2 lines below are wrong - that is not what is returned.
    # But since it is never used as an input, 
    # we dont even know that that is what is returned.
    ops.expression.return_value = "expr(1, 2)"
    ops.concatenation.return_value = "concat(1, 2)"

    print_spy = mocker.patch("examples.basics.print")

    b.do_ops(ops, 1, 2)

    ops.plus.assert_called_once_with(1, 2)
    ops.expression.assert_called_once_with(1, 2)
    ops.concatenation.assert_called_once_with(1, 2)
    assert [call.args for call in print_spy.call_args_list] == snapshot



def test_do_ops_DI_with_protocol_mock(mocker, snapshot):
    ops = mocker.create_autospec(b.BasicOps, instance=True, spec_set=True)
    ops.plus.return_value = 3
    # ops.expression.return_value = "expr(1, 2)"
    # ops.concatenation.return_value = "concat(1, 2)"

    # print_spy = mocker.patch("examples.basics.print")

    returned = b.do_ops_DI(ops, 1, 2)

    ops.plus.assert_called_once_with(1, 2)
    # ops.expression.assert_called_once_with(1, 2)
    # ops.concatenation.assert_called_once_with(1, 2)

    # assert [call.args for call in print_spy.call_args_list] == snapshot

    assert returned == snapshot