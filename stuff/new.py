OUTPUT_TYPES = (str, int)
OUTPUT_TYPE = OUTPUT_TYPES[1]

class Any(object):
    def __repr__(self):
        if OUTPUT_TYPE == OUTPUT_TYPES[0]:
            return f"{str(self)}"
        elif OUTPUT_TYPE == OUTPUT_TYPES[1]:
            return f"{self.__strint__()}"

class Undefined(Any):
    v = None
    # Invert value
    def __invert__(self):
        return Defined(abs(self))
    
    def __abs__(self):
        return self.v
    
    def __str__(self) -> str:
        return "N"
    
    def __strint__(self) -> str:
        return "0"

class Defined(Undefined):
    v : Any
    def __init__(self, v):
        self.v = v

    def __invert__(self):
        return Defined(not self.v)
    
    def __mul__(self, other):
        if isinstance(other,Defined):
            result = []
            result.append(Defineable((self,self)))
            result.append(Defineable((self,other)))
            result.append(Defineable((other,self)))
            result.append(Defineable((other,other)))
            return Defineable(tuple(result))
        return Undefined()
    
    def __add__(self, other):
        if isinstance(other,Defined):
            return Defined(self.v + other.v)
        return self
    
    def __str__(self):
        if self.v is None:
            return "U"
        if self.v == True:
            return "[T]"
        else:
            return "[F]"

    def __strint__(self , num : bool = True):
        if self.v is None:
            return "1"
        if self.v == True:
            return "[1]"
        else:
            return "[0]"

class Defineable(Defined):
    def __mul__(self, other):        
        result = []
        if isinstance(other,Defineable):
            for i in self.v:
                for j in other.v:
                    result.append(Defineable((i,j)))
            return Defineable(tuple(result))
        return Undefined()
    

    def __str__(self):
        return f"[{self.v[0]},{self.v[1]}]"
    
    def __strint__(self):
        return f"[{self.v[0].__strint__()},{self.v[1].__strint__()}]"


universe :list = []
dnone = Undefined()
dunary = ~dnone
dbinary0 = ~dunary
dbinary1 = ~dbinary0
dtuple = dbinary0 * dbinary1
dtriple = dtuple * dtuple.v[1]  

universe.append(dnone)
universe.append(dunary)
universe.append(dbinary0)
universe.append(dbinary1)
universe.append(dtuple)
universe.append(dtriple)


print(universe)