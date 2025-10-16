


import os
from pathlib import Path
import src.capture.capture as c
cch = c.CaptureHandler

from examples.BasicOps_interface import BasicOps

import examples.basics_module as bm

def CE():
    return os.getenv("SNAPY_CAPTURE_ENABLED") == "1"
    
class RealOpsOne:

    @c.capture(in_capture_mode=CE())
    def plus(self, a, b, c=1, d=2):
        return a + b + c + d

    @c.capture(in_capture_mode=CE())
    def concatenation(self, a, b):
        return str(a) + str(b)

    def expression(self, a, b):
        return self.concatenation(a, a * b + (a - b) / self.plus(a, b))


class RealOpsTwo:

    def plus(self, a, b, c=1, d=2):
        return a

    def concatenation(self, a, b):
        return str(a)

    def expression(self, a, b):
        return self.concatenation(a, self.plus(a, b))

def do_ops(ops: BasicOps, a, b):
      print(ops.plus(a, b, c=8))
      print(ops.expression(a, b))
      print(ops.concatenation(a, b))

# @c.capture(target_path=(Path("capture") / Path(__file__).resolve().parent / "basics" / "do_ops_DI"), in_capture_mode=CE())
@c.capture(in_capture_mode=CE())
def do_ops_DI(ops: BasicOps, a, b):
    i = ops.plus(a, b)
    j = ops.expression(i, b)
    k = ops.concatenation(i, j)
    print(k)
    return "start" + k


def main():
    print(do_ops(RealOpsOne(), 1, 2))
    print('---')
    print(do_ops(RealOpsTwo(), 5, 3))
    print('---')
    print(do_ops_DI(RealOpsOne(), 1, 2))
    print('---')
    print(do_ops_DI(RealOpsOne(), 5, 3))

if __name__ == "__main__":

    print("cch.get_func_path_id(RealOpsOne.plus):")
    print(cch.get_func_path_id(RealOpsOne.plus))

    print("cch.get_func_path_id(bm.RealOpsThree.plus):")
    print(cch.get_func_path_id(bm.RealOpsThree.plus))

    print("cch.get_func_path_id(bm.do_ops_DI_two):")
    print(cch.get_func_path_id(bm.do_ops_DI_two))



    import os
    import dotenv
    dotenv.load_dotenv()
    print("------------------------------")
    print(os.getenv("SNAPY_CAPTURE"))

    main()
