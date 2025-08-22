import json
from typing import TypeVar, Generic
# Genesis 1:1 ( create identity for abstraction )
EARTH = TypeVar("EARTH")

class Heaven(Generic[EARTH]):
    def __init__[EARTH](self, *v : EARTH):
        self.__slots__ = "v"
        self.v = v
        
    def __or__(self, other: EARTH):
        if self == other:
            return other
        else:
            return self

    def __eq__(self, other: EARTH) -> bool:
        if isinstance(other, Heaven):
            return self.v == other.v
        return self.v == other

    def __len__(self):
        return len(self.v)

    def __iter__(self):
        if hasattr(self.v,'__iter__'):
            return iter(self.v)
        return StopIteration

    def __repr__(self):
        if self.v is VOID:
            return f"VOID"
        r = f"[I:{self.int()}"
        r += f"R:{self.real()}"
        r += f"V:{self.vector()}]"
        #r = f"{self.vector()}"
        return r
    
    def __str__(self):
        return str(self.v)
    
    def __add__(self, other: EARTH) -> 'Heaven[EARTH]':
        result = self
        for i in result:
            if i is None:
                result[i] = other
        return result
        
    
    def __matmul__(self, other: EARTH) -> 'Heaven[EARTH]':
        res = ((self + self),
               (self + other),
               (other + self),
               (other + other))
        return Heaven(*res)
    
    def __mul__(self, other: EARTH) -> 'Heaven[EARTH]':
        result = self
        for i in self:
            for j in other:
                result = Heaven[result](result)
        return result
    
    def int(self):
        return self._int() - 2
    
    def real(self):
        return self._int()
               
    def tuple(self):
        return tuple([v for v in self])
    @staticmethod
    def _subcheck(val, current = 0):
        
        if (val is not None) and hasattr(val,'v') and hasattr(val.v,'__iter__'):
            for i in val.v:
                return Heaven._subcheck(i, current + 1) 
        else:
            return current + 1
        
    def _int(self):
        return Heaven._subcheck(self)        

    def dim(self):
        r = ELECTRON
        if self.v is not None:
            for i in self:
                if i is not None:
                    r = Heaven[r](r)
        return r
    
    @staticmethod
    def vector_single(self):
        r = ""
        for i in self.v:
            if i is Heaven:
                r+= f"[[1],{Heaven.vector_single(i)},]"
        if r == "":
            r = "0"
        return r
    
    def vector(self):
        return Heaven.vector_single(self)


u = []

#Genesis 1:1
VOID : EARTH = None
#Genesis 1:2
Create = Heaven[VOID]
PHOTON = Create(VOID)
UNITY = Heaven[None](None)
FALSE = Heaven[UNITY](UNITY)
Identity = Heaven[PHOTON]

ELECTRON = Identity(PHOTON)
Invert = Heaven[ELECTRON]

ELECTRIC_CHARGE = ELECTRON,POSITRON = ELECTRON,Invert(ELECTRON)

Rotate = Heaven[POSITRON]

RED = Rotate(POSITRON)
GREEN = Rotate(RED)
BLUE = Rotate(GREEN)

print(VOID)
print("----")
print(PHOTON)
print("----")
print(ELECTRON)
print("----")
print(POSITRON)

print(RED)
print("----")
print(GREEN)
print("----")
print(BLUE)


print("----")
print(PHOTON.int())
print("----")
print(ELECTRON.int())
print("----")
print(POSITRON.int())
print("----")
print(RED.int())
print("----")
print(GREEN.int())
print("----")
print(BLUE.int())
