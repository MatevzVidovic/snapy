import src.capture.capture as c
from examples.BasicOps_interface import BasicOps

cch = c.CaptureHandler


class RealOpsThree:
    @c.capture()
    def plus(self, a, b, c=1, d=2):
        return a + b + c + d

    @c.capture()
    def concatenation(self, a, b):
        return str(a) + str(b)

    def expression(self, a, b):
        return self.concatenation(a, a * b + (a - b) / self.plus(a, b))


def do_ops_DI_two(ops: BasicOps, a, b):
    i = ops.plus(a, b)
    j = ops.expression(i, b)
    k = ops.concatenation(i, j)
    print(k)
    return "start" + k
