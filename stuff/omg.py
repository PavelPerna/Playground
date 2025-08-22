from itertools import product
import math

class Printable(object):
    def __repr__(self):
        result = ""
        for itm in self.__dict__: 
            i = self.__dict__[itm]
            #if i is object and issubclass(i, Printable) or isinstance(i, Printable):
            result+= f"{itm}:{i}\r\n"
        return result

class Dimensional(Printable):
    def __init__(self, dim :int = None,base = None):
        self.__dim = 0 if dim is None else dim
        if base:
            self.__dim = base.dim()
        self._target_dim = self.__dim + 1
        self._base = base
        self._unfolded = False
    

    def dim_raise(self):
        self.__dim = self.__dim + 1

    def dim(self):
        return self.__dim   
    
    def _unfold_start(self, *args,**kwargs):
        return type(self)(base=self,*args,**kwargs)
        
    def _unfold_end(self, *args,**kwargs):
        self.dim_raise()
        self._unfolded = True
        return True

    def isClass(self,val):
        return type(val) == type

    def unfold(self, *args, **kqargs):
        print("Unfolding",type(self),self.dim())
        for ev in self.__dict__:
            if ev in ['_base','before']:
                continue
            ei = self.__dict__[ev]
            if ei is object and issubclass(ei, Dimensional) or isinstance(ei, Dimensional):
                if not ei._unfolded:
                    ei.unfold()
        self._unfold_end()
        result = self._unfold_start( *args, **kqargs)
        return result
        

    def reset(self):
        print("Reseting",type(self),self.dim())
        for ev in self.__dict__:
            ei = self.__dict__[ev]
            if ei is object and issubclass(ei, Dimensional) or isinstance(ei, Dimensional):
                ei._unfolded = False  

class Variable(Dimensional):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.values = self.generate()

    @classmethod
    def dot(var1 , var2):
        return [var1,var2]

    @classmethod
    def product(var1, var2):
        result = []
        for prop1 in var1:    
            for prop2 in var2:
                result.append(Variable.dot(prop1,prop2))         
        return result

    def generateValues(self):
        values = []
        dim = self.dim()
        match dim:
            case 0:
                values = [None,[None]]
            case n:
                values = Variable.product(self._base.values, self._base.values)

        return values


    def generate(self):
        values = self.generateValues()
        print(f"{self.dim()} Values {values}")
        return values


    def unfold(self, *args, **kqargs):
        print("Unfold var",self.dim())
                #result[f"{i+1}"] = 0.0 if i == 0 else math.log(i+1,self.dim()+1)
        #return Variable(dim=self._target_dim,base=self,values=values)
        self._unfold_end()
        result = self._unfold_start( *args, **kqargs)
        return result
        
    

class Group(Dimensional):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._variable = Variable(dim=self.dim(),base= None if self._base is None or self._base._variable is None else self._base._variable)

    def unfold(self, *args, **kqargs):
        print("Unfold group",self.dim())
        result = self._unfold_start( *args, **kqargs)
        result._variable = self._variable.unfold()
        self._unfold_end()
        return result
        

class Algebra(Dimensional):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._group = Group(base=None if self._base is None or self._base._group is None else self._base._group,dim=self.dim())
        self._operations = {}

    def unfold_operations(self):
        print("Unfold algebraic operations",self.dim())
        #print(self._group._variable)
        #for val,val2 in product(self._group._variable,self._group._variable):
            #print(f"[{self._group._variable[val]},{self._group._variable[val2]}]")
        #    print(f"[{val},{val2}]")

        return self._operations

    def unfold(self, *args, **kqargs):
        print("Unfold algebra",self.dim())
        result = self._unfold_start( *args, **kqargs)
        result._group = self._group.unfold(*args, **kqargs)
        result.unfold_operations()
        self._unfold_end()
        return result
                
                


class Universe(Dimensional):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._algebra = Algebra(base=None if self._base is None or self._base._algebra is None else self._base._algebra)

    def conceptualize(self):
        return

    @property
    def value(self):
        return self._base


try:
    u = Universe(base=None)
    i = 0
    while i in range(3):
        u.reset()
        u = u.unfold()
        i+=1

except Exception as e:
    print(e)