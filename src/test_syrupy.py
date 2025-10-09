
import examples.basics as b

# tests/test_greeting.py
def test_do_ops(snapshot):

    returned = b.do_ops(b.RealOpsOne(), 1, 2)
    assert returned == snapshot