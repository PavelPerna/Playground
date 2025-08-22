import ctypes


OT = 0x0
OUTPUT_TYPES = (
    0x0,  # FULL 
    0x1   # INT
)
OUTPUT_TYPE = OUTPUT_TYPES[OT]

class Abstract:...  # Service class


class Earh:...  # Void / Undefined / None
class Heaven:... # Identity element
class Value:... # Scalar / Variable
class Container:...# Container / List / Array

type UniverseValues = ( Null | Unity | Value | Container )
type UniverseContainers = ( Container )
type UniverseTypes = ( UniverseValues | UniverseContainers )

class Quanternion(object):
    actions_default = {
        UniverseTypes: lambda *x: x,
    }
    def __init__(self, actions : dict = None):
        self.actions = self.actions_default
        if actions is not None:
            self.actions.update(actions)
        
    def __call__(self, left = None, right = None):
        index = type(left if right is None else right)
        action = self.actions[index]
        return  action((Null, left, (left,right))[self.actions.__code__])
        
class Abstract(object):
    def __repr__(self):
        return f"{self}"
    
    def __str__(self) -> str:
        return Quanternion({
            Null : "Void" if OT == 0 else "",
            Unity : "Singularity" if OT == 0 else "[]",           
            Value : lambda x: f"Value[{x.v}])" if OT == 0 else f"[{int(x.v)}]" ,                
            Container : lambda x: f"Container[{x.v[0]},{x.v[1]}]" if OT == 0 else f"[{int({x.v[0]})},{int({x.v[1]})}]"
        })(self)
            
    @staticmethod
    def dim(what):
        return Quanternion({
            Null: lambda :Value(Null),
            Unity:lambda :Value(0),
            Value:lambda :Value(1),
            Container:lambda x:Value(Abstract.tdim(x.v))
        })(what)
         
    @staticmethod
    def shape(what):
        if type(what.v) is Container: 
            return Container(what.v[i].shape() for i in what.v)
        return Container(i for i in range(Abstract.dim(what)))
        
    @staticmethod
    def cross(left : Container, right: Container ):
        return Container((i,j) for i in left.v for j in right.v)
    
    @staticmethod
    def tdim(t: tuple):
        return Value(Abstract.tdim((tuple(v) if type(v) is not tuple else v for v in t)))
        
    @staticmethod
    def from_value(val):
        return Quanternion({
            Null | Unity | Value : lambda x : Unity() if x == None else Value(x)
        })(val)
    
""" Main code"""

class Null(Abstract):
    def __init__(self):
        self.b = 0x0
    def __invert__(self):
        return Unity()

class Unity(Null):
    def __init__(self):
        super().__init__()
        self.v = Null()
        self.b+= 0x1

    def __invert__(self):
        return Value(type(self.v) is Null)

    def __add__(self, other):
        return other
    
    def __mul__(self, other):
        return other
    
    def __matmul__(self, other):
        par = self,other
        if type(other) is Container:
            par = self.cross(self, other)
        return Container( par )

class Value(Unity):
    def __init__(self, v: Unity = Null()):
        super(Value, self).__init__()
        self.v = v
        self.b &= 0x1

    def __add__(self, other):
        return Quanternion(
            { 
                Unity: lambda x, y : Value(x.v + y.v),
                Value: lambda x, y : Value(x.v + y.v)
            }
        )(self, other)
    
    def __mul__(self, other):        
        return Quanternion(
            {
                Value: lambda x, y : Value(x.v * y.v)
            }
        )(self, other)
    
    def __matmul__(self, other):
        return Quanternion(
            {
                (Null | Unity | Value): lambda x, y: Container( x, y )
            }
        )(self, other)


class Container(Value):
    def __init__(self, *args, **kwargs):
        super(Container, self).__init__()
        new = []
        b = self.b
        for arg in args:
            a = Value().from_value(arg)
            b+= a.b
            new.append(a)
            
        self.v = tuple(new)
        self.shape = Abstract.shape(self)
        self.b = 0x2 + b

    def __abs__(self):
        return Container(abs(i) for i in self.v)
    
    def __matmul__(self, other):
        return Quanternion({
                (Null, Unity, Value) : lambda x,y : super().__matmul__(x,y),
                Container: lambda x,y : self.cross(x,y)
            }
        )(self, other)        

universe :list = []
# 0 - 0 
dvoid = Null()
# 0 - 1
dunity = ~dvoid
# 1 - 0
dbinary = dunity @ dvoid
# 1 - 1
# 2 - 0
dtuple = dbinary @ dunity
dtriple = dbinary @ dbinary
# 2 - 1
dtuples = dtuple @ dtuple
print(dtuples.shape())
# 2 - 2
dtriple = dtuple @ dbinary
dtriples = dtuples @ dtuple

universe.append(dvoid)
universe.append(dunity)
universe.append(dtuple)
universe.append(dtuples)
universe.append(dtriples)

print(universe)
OT = 1
print(universe)