import array
class Oper(object):
    def __init__(self, func):
        self.func = func
        self.dim = func.__code__.co_argcount

    class RBind:
        def __init__(self, func, bound):
            self.func = func
            self.bound = bound 
        def __call__(self, other):
            return self.func(other, self.bound)
        __ror__ = __call__

    class LBind:
        def __init__(self, func, bound):
            self.func = func
            self.bound = bound
        def __call__(self, other):
            return self.func(self.bound, other)
        __or__ = __call__

    def __or__(self, other):
        if self.func.__code__.co_argcount == 1:
            return self.func(other)
        return self.RBind(self.func, other)

    def __ror__(self, other):
        if self.func.__code__.co_argcount == 1:
            return self.func(other)
        return self.LBind(self.func, other)

    def __call__(self, *args):
        return self.func(*args)

@Oper
def NOT(a):
    t = type(a)
    if t is None:
        return False
    if t is int:
        return 1 if a == 0 else 0
    if t is bool:
        return not a
    if t is tuple:
        return tuple(NOT | i for i in a)
        

@Oper
def MUL(a,b):
    return (a,b)

print(f"{NOT | 0 | MUL | (NOT | (1, NOT | 1))}")
print(f"{NOT | 0 | MUL | (1,0)}")
a = array.array(0,1)
b = array.array(0,1)
print(a @ b)