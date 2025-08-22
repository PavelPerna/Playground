import torch
from torch import Tensor

TensorTrue : Tensor = Tensor([float(int(True))])
TensorFalse : Tensor = Tensor([float(int(False))])    

class Variable(object):
    def __init__(self):
        self.tensor = Tensor()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class TensorStore(object):
    def __init__(self):
        # Dictionary to store tensors by dimensionality (0D, 1D, 2D, etc.)
        self.__tensors = []

    def process(self, tensor : Tensor):
        """Store a tensor, categorized by its dimensionality."""
        if not any(torch.equal(tensor, existing) for existing in self.__tensors):
            self.__tensors.append(tensor)

    def tensors(self):
        return self.__tensors if len(self.__tensors) > 0 else [TensorFalse]
                                                         

    def state(self) -> Tensor:
        """Return all tensors across all dimensions."""
        return self.tensors()

    def __len__(self):
        """Return total number of tensors stored."""
        return len(self.__tensors)

    def __repr__(self):
        """String representation of stored tensors by dimension."""
        return f"Tensors : {self.__tensors}"
    
EventID = int

class Event(object):
    def __init__(self, name : str, id : EventID):
        self.id = id if id else len(Events())
        self.name = name 

class Events(object,metaclass=Singleton):  
    NOOP : EventID = 0
    OBSERVE : EventID = 1
    def __init__(self):
        self._events : dict = {}
        for name, evn in self.__dict__ and evn is EventID:
            self._events[name] = Event(name=name,id=evn)

    def getEventList(cls):
        return cls._events

    def __len__(self):
        if hasattr(self._events,'__len__'):
            return len(self._events) 
        return 0   

class Action(object):
    def __init__(self, actors : list , action_id: bool = Events.OBSERVE, targets : list = None):
        super().__init__()
        self.id = action_id
        self.actors = actors
        if targets is None:
            targets = [Universe()]
        self.targets = targets
    

    def perform(self):
        observation = []
        for target in self.targets: 
            observation.append(target.reaction(self))
        return observation
       
# Anything that exist
class Entity(object):
    def __init__(self, initial_tensors=[]):
        self.tensor_store = TensorStore()
        for tensor in initial_tensors:
            self.tensor_store.process(tensor)

# Anything that exist and have energy
class Energy(Entity):
    def __init__(self, initial_tensors=[], energy = tuple):
        super().__init__(initial_tensors)
        self.__energy = energy

# Anything that can perform actions
class Actor(object):

    def act(self, action : Action,actor_as_target: bool = False):
        # Default value for targets
        if action.targets is None:
            action.targets = [Universe()]
        # If action should be performed on actor as well ( usually OBSERVE observers targets and then actor after observation as well )
        if actor_as_target and self not in action.targets:
            action.targets.append(self)
        
        if action.actors is None:
            action.actors = [self] 

        return action.perform()


class Reactor(object):

    def reaction(self, action : Action):
        if action.id == Events.OBSERVE:
            return self.tensor_store.state()           
        return TensorFalse

class Universe(Energy, Actor, Reactor, metaclass=Singleton):
    pass

class Consciousness(Energy, Actor, Reactor):
    def __init__(self):
        initial_tensors = [TensorTrue if bool(self) else TensorFalse]
        super().__init__(initial_tensors)

    def observe(self):
        observe_action = Action(action_id=Events.OBSERVE,actors=[self],targets=[Universe(),self]) 
        data = self.act(observe_action)
        for item in data:
            for tensor in item:
                self.tensor_store.process(tensor)
        self.__conceptualize()
        return data

    def __conceptualize(self):
        print("Tensors by dimensionality:")
        tensors = self.tensor_store.tensors()
        for i, t in enumerate(tensors):
            print(f"  Tensor {i}: shape {t.shape}, values {t}")
        # Sample operation: Cartesian product for 1D tensors
        if len(tensors) > 1:
            prod = torch.cartesian_prod(*tensors)
            print(f"  Cartesian product: {prod}")
            self.tensor_store.process(prod)


if __name__ == "__main__":
    universe = Universe()
    consciousness = Consciousness()
    for _ in range(1):
        consciousness.observe()
    print(consciousness.tensor_store.state())
