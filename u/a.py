from typing import TypeVar, Generic
EARTH = TypeVar("EARTH")


class Heaven(Generic[EARTH]):
    def __init__[EARTH](self, *v : EARTH):
        self.__slots__ = "v"
        self.v = v
        
    def __eq__(self, other: EARTH) -> bool:
        if isinstance(other, Heaven):
            return self.v == other.v
        return self.v == other

    def __iter__(self):
        if hasattr(self.v,'__iter__'):
            return iter(self.v)
        return iter([])

    def __repr__(self):
        return f"{self.dim()}"
    
    def __str__(self):
        return str(self.v)
    
    def __add__(self, other: EARTH) -> 'Heaven[EARTH]':
        if other is None:
            return self
        return Heaven[self](*(self.v + other.v))
    
    def __matmul__(self, other: EARTH) -> 'Heaven[EARTH]':
        res = ((self + self),
               (self + other),
               (other + self),
               (other + other))
        return Heaven(*res)
    
    def __mul__(self, other: EARTH) -> 'Heaven[EARTH]':
        none = Heaven[None](None)
        if other == none:
            return other
        r = other
        for _ in range(self.dim()):
            r += other 
        return r

    def dim(self) -> int:
        if hasattr(self, 'v'):
            if isinstance(self.v, tuple):
                for i in self.v:
                    if type(i) is Heaven:
                        return 1 + i.dim()
        return 0
    
    def __val__(self):
        c = TUPLE0
        for i in self:
            c *= i
        return c


VOID = Heaven[None](None)
SINGULARITY = Heaven[VOID](VOID)
TUPLE0 = Heaven[SINGULARITY](SINGULARITY)
TUPLE1 = Heaven[TUPLE0](TUPLE0)
TRIPLET0 = Heaven[TUPLE1](TUPLE1)
TRIPLET1 = Heaven[TRIPLET0](TRIPLET0)
TRIPLET2 = Heaven[TRIPLET1](TRIPLET1)

print(VOID, SINGULARITY, TUPLE0, TUPLE1, TRIPLET0, TRIPLET1, TRIPLET2)

# Dim None
e : EARTH = None
# Dim 0
h0 = Heaven[e](e)
# Dim 1
h1 = Heaven[h0](h0)
h2 = Heaven[h1](h1)
# Dim 2
h3 = h1 + h1
h4 = h1 + h2
h5 = h2 + h1
h6 = h2 + h2

h7 = h1 * h1
h8 = h1 * h2
h9 = h2 * h1
h10 = h2 * h2

print(e,h0,h1,h2, h3,h4,h5,h6,h7,h8,h9,h10)