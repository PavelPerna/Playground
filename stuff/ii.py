class Any(object):
    
    def __str__(self, num : bool = False) -> str:
        r ="\n"
        r+= f"[{str(self.v)}]"
        return r
    def __repr__(self):
        return f"{str(self)}"

class Undefined(Any):
    v = None
    # Invert value
    def __invert__(self):
        return Defined(abs(self))
    
    def __abs__(self):
        return self.v
    
    def __str__(self, num : bool = False):
        return "N"



class Defined(Undefined):
    v : Any
    def __init__(self, v):
        self.v = v

    def __invert__(self):
        return Defined(not self.v)
    
    def __mul__(self, other):
        if isinstance(other,Defined):
            return Defineable((self,other))
        return Undefined()
    
    def __add__(self, other):
        if isinstance(other,Defined):
            return Defined(self.v + other.v)
        return self
    
    def __str__(self , num : bool = True):
        if self.v is None:
            return "U"
        if self.v == True:
            return "[True]" if not num else "[1]"
        else:
            return "[False]" if not num else "[0]"

    
class Defineable(Defined):
    def __mul__(self, other):        
        result = []
        if isinstance(other,Defineable):
            for v in self.v:
                for j in other.v:
                    result.append(v * j)
                    result.append(j * v)
            return Defineable(tuple(result))
        if isinstance(other,Defined):
            for i in self.v:
                result.append((i * other))
                result.append((other * i))
            return Defineable(tuple(result))
        return Undefined()
    
    def __add__(self, other):
        if type(other) is not tuple:
            other = (other,)
        self.v.__add__(other)

    def __str__(self, num : bool = False):
        r = ""
        r += f"[{self.v[0]},{self.v[1]}]"
        return r

universe :list = []
dnone = Undefined()
universe.append(dnone)
dunary = ~dnone
universe.append(dunary)
dbool0 = ~dunary
universe.append(dbool0)
dbool1 = ~dbool0
universe.append(dbool1)
dbinary0 = dbool0 * dunary
universe.append(dbinary0)
dbinary1 = dbool1 * dunary
universe.append(dbinary1)
dcolor1 = dbinary0 * dunary
universe.append(dcolor1)
dcolor2 = dbinary0 * dbool0 * dunary 
universe.append(dcolor2)
dcolor3 = dbinary0 * dbool1 * dunary 
universe.append(dcolor3)
dcolor4 = dbinary1 * dunary
universe.append(dcolor4)
dcolor5 = dbinary1 * dbool0 * dunary 
universe.append(dcolor5)
dcolor6 = dbinary1 * dbool1 * dunary
universe.append(dcolor6)
print((dbinary0*dunary))
print(universe)
"""
class Any(Defined):
    pass

class Container(Any):    
    dim = 0
    def __init__(self, items: tuple[Any] = Undefined):
        self.length = 0
        self.head = Undefined
        if items is not Undefined:
            for item in items:
                self += Reference.into(item)
        
    def __getitem__(self, index):
        iterator = iter(self)
        for i in iterator:
            if iterator.processed==index+1:
                return i
        raise Exception('Index out of range')

     
    def __add__(self, val):
        return self + val    
    
    def __iadd__(self, val):
        return Container.__add_lowlevel(self, val)
    
    def __sub__(self, val):
        if type(val) != Value:
            val = Value(value=val)
        current = self.head
        prev = Undefined
        while current:
            if current.v == val:
                if prev:
                    prev.next = current.next
                else:
                    self.head = current.next
                self.length -= 1
                break
            prev = current
            current = current.next
        return self
    
    def __iter__(self):
        return ContainerIterator(self)

    def __str__(self):
        items = [str(i) for i in self]
        return f"[{', '.join(reversed(items))}]"
    
    def __get__(self, instance , owner):
        return self
        

    def __mul__(self, other: Any):
        result = self * other
        return result

    @staticmethod
    def __compare(x, y):
        for i in x:
            for j in y:
                found = False
                if i == j:
                    found = True
                if not found:
                    return False
        return True
        
    def __eq__(self, other):
        if other is Undefined:
            return self.length == 0
        if type(other) != Container:
            other = Container.into(other)
        return self.__compare(self, other) and self.__compare(other, self)
    
    @staticmethod
    def into(what):
        if type(what) == tuple:
            res = Container()
            for w in what:
                res+=w
            what = res
        if type(what)!=Container:
            if type(what)!=Reference:         
                what = Reference.into(what)
            what = Container((what,))
        return what

class ContainerIterator(Any):
    def __init__(self, container):
        self.current = container.head
        self.processed = 0
        self.length = container.length
    
    def __iter__(self):
        self.processed = 0
        return self
    
    def __next__(self):
        if self.current is Undefined or self.processed >= self.length:
            raise StopIteration
        value = self.current.__get__(self.current,self.current)
        self.current = self.current.next
        self.processed += 1
        return value
    
class Value(Any):
    def __init__(self, value: Any = Undefined):
        self.v = value

    def __str__(self):
        return str(self.v) if self.v not in [Undefined] else "Undefined"
    
    def __add__(self, other):
        if type(other)!=Value:
            other = Value(value=other)
        return Value(self.v + other.v)
    
    def __iadd__(self, other):
        if type(other)!=Value:
            other = Value(value=other)
        self.v += other.v
        return self
    
    def __eq__(self, other):
        if type(other)!=Value:
            return False
        return self.v == other.v
    
    def __str__(self):
        return str(self.v)
    
    def __mul__(self, other):
        if isinstance(other, Container):
            return other * self
        if isinstance(other, Value):
            return Reference(Container((self.v,other.v)))
        
    def is_scalar(self):
        return not isinstance(self.v, Container)
    
    def __mul__(self,other):
        if other is Undefined:
            other = 0x0

        return Container((self,other))
     
    @staticmethod
    def into(what):
        if type(what)==Value:
            return what
        elif type(what) == tuple:
            return Value(what[0])
        else:
            return Value(what)
    
class Function(Any):
    def __init__(self, f: callable):
        self.f = f

    def __call__(self, *args, **kwargs):
        self.f(*args, **kwargs)
        
    def __str__(self):
        code = self.f.__code__
        name = code.co_name
        args = code.co_varnames
        argcount = code.co_argcount
        return json.dumps({
            'name': name,
            'args': {
                'count': argcount,
                'names': args
            }
        })

class Reference(Any):
    def __init__(self, value: Value):
        super().__init__(value=value)
        self.next = Undefined
    
    def __str__(self):
        return str(self.v)

    def __get__(self, instance, owner):
        return super().__get__(instance, owner)

    @staticmethod
    def into(what: Any):
        if type(what) == Reference:
            return what
        if type(what) in (Value, Container):
            return Reference(what)
        else:
            return Reference(Value.into(what))
        
class Universe(Container):
    def __init__(self, items = Undefined):
        super().__init__(items)
    pass

class Consciousness(Universe):
    def __call__(self, universe: Universe):
        defineable = universe  
        unfolder = Container.into(0x1)
        defined = defineable * unfolder
        universe += Reference.into(defined)
        print(str(universe))
        return universe

# Test code
if __name__ == "__main__":
    u = Universe()
    c = Consciousness()
    u = c(u)  # First iteration
    u = c(u)  # Second iteration
    u = c(u)  # Third iteration
    u = c(u)  # Third iteration
    """