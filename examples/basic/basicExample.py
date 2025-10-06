



def inner(arg1, arg2):
    return arg1 + arg2

def outer(arg3, arg4):
    return arg3 + arg4 + inner(arg3, arg4)


def main():
    print(outer("ena", "dva"))

main()

