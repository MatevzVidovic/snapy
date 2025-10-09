


from typing import Protocol, runtime_checkable
import src.capture.capture as c

@runtime_checkable
class BasicOps(Protocol):
    def plus(self, a, b): ...
    def plusSpecific(self, a: int, b: float): ...
    def concatenation(self, a, b) -> str: ...
    def expression(self, a, b): ...


    
class RealOpsOne:

    @c.capture()
    def plus(self, a, b):
        return a + b

    @c.capture()
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

def do_ops_DI(ops: BasicOps, a, b):
    i = ops.plus(a, b)
    j = ops.expression(i, b)
    k = ops.concatenation(i, j)
    print(k)
    return "start" + k


def main():
    print(do_ops_DI(RealOpsOne(), 1, 2))
    print('---')
    print(do_ops_DI(RealOpsOne(), 5, 3))
    print('---')
    print(do_ops(RealOpsOne(), 1, 2))
    print('---')
    print(do_ops(RealOpsTwo(), 5, 3))

if __name__ == "__main__":
    main()


    import os
    import dotenv
    dotenv.load_dotenv()
    print("------------------------------")
    print(os.getenv("SNAPY_CAPTURE"))

