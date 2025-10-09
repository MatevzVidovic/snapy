


from typing import Protocol, runtime_checkable

@runtime_checkable
class BasicOps(Protocol):
    def plus(self, a, b): ...
    def plusSpecific(self, a: int, b: float): ...
    def concatenation(self, a, b) -> str: ...
    def expression(self, a, b): ...


    
class RealOpsOne:

    def plus(self, a, b):
        return a + b

    def concatenation(self, a, b):
        return str(a) + str(b)

    def expression(self, a, b):
        return self.concatenation(a, a * b + (a - b) / self.plus(a, b))


class RealOpsTwo:

    def plus(self, a, b):
        return a

    def concatenation(self, a, b):
        return str(a)

    def expression(self, a, b):
        return self.concatenation(a, self.plus(a, b))

def do_ops(ops: BasicOps, a, b):
    print(ops.plus(a, b))
    print(ops.expression(a, b))
    print(ops.concatenation(a, b))


def main():
    do_ops(RealOpsOne(), 1, 2)
    print('---')
    do_ops(RealOpsTwo(), 5, 3)


main()

