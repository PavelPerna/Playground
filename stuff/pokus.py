import torch
from itertools import product
from torch import Tensor

class Algebra(object):
    def __init__(self):
        self.to = {
            0:lambda x: None,
            1:lambda x:bool(x),
            2:lambda x:float(x),
            3:lambda x:Tensor(x)
        }
        self.equals = {
            0: lambda x: True,
            1: lambda x,y: bool(x == y),
            2: lambda x,y : bool(x == y),
            3: lambda x,y : bool(torch.equal(x,y))
        }
        self.algebra = {}
        self.algebra[0] = {}
        self.algebra[1] = {
            "NOT": lambda x,y=False,i =False: ~ x if not i else ~~x,
            "AND":lambda x,y,i =False: x & y if not i else ~ (x & y),
            "OR":lambda x,y,i =False: x | y if not i else ~ (x | y),
            "XOR":lambda x,y,i =False: x ^ y if not i else ~ (x ^ y),
        }
        self.algebra[2] = {
            "ADD": lambda x,y,i =False : x+y if not i else y-x,
            "SUBSTRACT": lambda x,y,i =False: x+(-y) if not i else y+(-x),
            "MULTIPLY": lambda x,y,i =False: x*y if not i else x/y,
            "DIVISION": lambda x,y,i =False: x/y if not i else x*y,  
            "MOD": lambda x,y,i =False: x % y if not i else x+y,
            "SHIFT_LEFT":lambda x,y,i =False: x << y if not i else x >> y,
            "SHIFT_RIGHT" : lambda x,y,i =False: x >> y if not i else x << y,
            "COMPLEMENT" : lambda x,y,i =False: y-x if not i else y+x,
        }
        self.algebra[3] = {
            "VECTOR_ADD" : lambda x,y,alpha=1 : torch.add(x,y,alpha=alpha),
            "VECTOR_SUB" : lambda x,y,alpha=1 : torch.sub(x,y,alpha=alpha),
            "VECTOR_MULTIPLY" : lambda x,y : torch.mul(x,y),
            "VECTOR_PRODUCT" : lambda x,y: torch.matmul(x,y)
        }

        

    def getOperations(self, dim = 1, all = False, all_lower = False):
        if all: 
            return self.algebra
        if not all_lower:
            return self.algebra[dim]
        
        result = {}
        for d in range(dim + 1):
            result = result  | self.algebra[d]
        return result
    
    def getEqual(self, dim = 1):
        return self.equals[dim]
    
    def getInto(self, dim = 1):
        return self.to[dim]
    
    def into(self, what, dim = 1):
        return self.to[dim](what)
    
class Entity(object):
    def __init__(self, data):
        self.data = data

    def _state(self):
        return self.data

    def dimension(self):
        if self.data == None: return 0
        if self.data is not Tensor: return 1
        if self.data is Tensor: return self.data.ndim

class EarthAndHeaven(Entity):
    @classmethod
    def grow(self, what) -> Tensor:
        return torch.tensor([bool(what)] if what is not Entity else what.data)    

# Everything that can be observed 
class Observable(EarthAndHeaven):   
    def observed(self) -> Tensor | bool:
        return self._state()
    
# Everything that can observe
class Observer(EarthAndHeaven):
    def observe(self, observable: Observable) -> Tensor | bool:
        return observable.observed()

class Universe(Observable):
    pass


class Consciousness(Observable, Observer):
    def __init__(self, data, target : callable):
        super().__init__(data)     
        self.target = target   

    def resolve(self, universe:Universe) -> bool:
        # 1. do the observations
        universe_data = self.observe(universe)
        my_data = self.observe(self)

        dim = self.dimension()
         
        potential = algebra[dim]["XOR"](my_data,universe_data)
        operations = algebra.getOperations(dim,all_lower=True)
        equals = algebra.getEqual(dim)     

        goal = self.target(universe_data)
        if dim == 1:
            potential = [potential]
            universe_data = [universe_data]
            my_data = [my_data]
            
        
        for p,u,m,o in product(potential, universe_data,my_data,operations):
            possible = False
            if not equals(u,m):
                u_new =operations[o](u,m)
                m_new =operations[o](m,u)
                potential_new = self.algebra[dim]["XOR"](u_new, m_new)
                if not equals(u_new,m_new) and equals(u_new,m) and equals (m_new,u):
                    

                print("Operation",o,u,m)    
                print("Universe + potential",u + p,"Me - potential", m ^ p)
                print("Universe_new - potential",u_new ^ p,"Me_new + potential", m + p)
                if (u  p == u_new) and (m ^ p == u) and (u_new ^ p == m_new) and (m_new + p == u_new):    
                    possible = True
                
            print(f"Possible :{possible}")
            print(f"----------------")

        


            

# Void
algebra = Algebra()
origin = None #It is nothin  
u = Universe(origin)

# Start 
origin = algebra.into(u.data, u.dimension()+1)
target = lambda x: not x

u = Universe(Universe.grow(origin))
c = Consciousness(Universe.grow(target(origin)), target) # It posess possibility of change but not concrete


#while True:
    #d = u.ndim
    #while u.ndim == d:

u = c.resolve(u)
    
    

