import torch
from torch import Tensor

TensorTrue: Tensor = Tensor([1.])
TensorFalse: Tensor = Tensor([0.])

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class DimensionalityManager(object):
    def __init__(self, current_dim=1):
        self.__current_dim = current_dim  # Private attribute

    def get_current_dim(self):
        """Get current dimension."""
        return self.__current_dim

    def validate_tensor(self, tensor):
        """Check if tensor's ndim <= current_dim."""
        return tensor.ndim <= self.__current_dim

    def set_current_dim(self, dim):
        """Update current dimension (for future use)."""
        self.__current_dim = dim

class TensorStore(object):
    def __init__(self, dimensionality_manager=None):
        self.__tensors = []
        self.__id_counter = 0
        self.dimensionality_manager = dimensionality_manager

    def process(self, tensor: Tensor):
        """Store a tensor with a unique ID if ndim <= max_dim."""
        if self.dimensionality_manager and not self.dimensionality_manager.validate_tensor(tensor):
            return None  # Reject tensor if ndim > current_dim
        if not any(torch.equal(tensor, existing) for _, existing in self.__tensors):
            tensor_id = self.__id_counter
            self.__tensors.append((tensor_id, tensor))
            self.__id_counter += 1
            return tensor_id
        return next(id_ for id_, t in self.__tensors if torch.equal(t, tensor))

    def tensors(self):
        """Return tensors, or empty list if none stored."""
        return [t for _, t in self.__tensors]

    def state(self) -> list[Tensor]:
        """Return all tensors."""
        return self.tensors()

    def __len__(self):
        """Return total number of tensors stored."""
        return len(self.__tensors)

    def __repr__(self):
        """String representation of tensors."""
        if not self.__tensors:
            return "No tensors stored"
        output = []
        for tensor_id, tensor in self.__tensors:
            label = "Existence" if torch.equal(tensor, TensorTrue) else "NonExistence" if torch.equal(tensor, TensorFalse) else str(tensor)
            output.append(f"Tensor {tensor_id}: shape {tensor.shape}, tensor[{label}]")
        return "\n".join(output)

EventID = int

class Event(object):
    def __init__(self, name: str, id: EventID):
        self.id = id
        self.name = name

class Events(object, metaclass=Singleton):
    NOOP: EventID = 0
    OBSERVE: EventID = 1

    def __init__(self):
        self._events: dict = {}
        for name, evn in self.__class__.__dict__.items():
            if isinstance(evn, int):  # Check for EventID
                self._events[name] = Event(name=name, id=evn)

    def getEventList(self):
        return list(self._events.values())

    def __len__(self):
        return len(self._events)

class Action(object):
    def __init__(self, actors: list, action_id: int = Events.OBSERVE, targets: list = None):
        self.id = action_id
        self.actors = actors
        self.targets = targets if targets is not None else [Universe()]

    def perform(self):
        observation = []
        for target in self.targets:
            observation.append(target.reaction(self))
        return observation

class Entity(object):
    def __init__(self, dimensionality_manager=None, initial_tensors=[]):
        self.tensor_store = TensorStore(dimensionality_manager)
        for tensor in initial_tensors:
            self.tensor_store.process(tensor)

class Energy(Entity):
    def __init__(self, dimensionality_manager=None, initial_tensors=[], energy=tuple()):
        super().__init__(dimensionality_manager, initial_tensors)
        self.__energy = energy

class Actor(object):
    def act(self, action: Action, actor_as_target: bool = False):
        if action.targets is None:
            action.targets = [Universe()]
        if actor_as_target and self not in action.targets:
            action.targets.append(self)
        if action.actors is None:
            action.actors = [self]
        return action.perform()

class Reactor(object):
    def reaction(self, action: Action):
        if action.id == Events.OBSERVE:
            return self.tensor_store.state()
        return [TensorFalse]

class Universe(Energy, Actor, Reactor, metaclass=Singleton):
    def __init__(self):
        super().__init__(DimensionalityManager(current_dim=1), initial_tensors=[TensorFalse])

class Consciousness(Energy, Actor, Reactor):
    def __init__(self, initial_tensors = [],initial_concepts = [],initial_energy = []):
        super().__init__(DimensionalityManager(current_dim=1), initial_tensors=initial_tensors)
        self.concepts_store = TensorStore(initial_concepts)  # No ndim limit for concepts
        self.energy_store = TensorStore(initial_energy)

    def observe(self):
        observe_action = Action(action_id=Events.OBSERVE, actors=[self], targets=[Universe(), self])
        data = self.act(observe_action, actor_as_target=True)
        for item in data:
            for tensor in item:
                self.tensor_store.process(tensor)
        self.__conceptualize()
        return data

    def __conceptualize(self):
        print("Tensors by dimensionality:")
        tensors = self.tensor_store.tensors()
        concepts = self.concepts_store.tensors()
        for i, t in enumerate(tensors):
            label = "Existence" if torch.equal(t, TensorTrue) else "NonExistence" if torch.equal(t, TensorFalse) else str(t)
            print(f"  Tensor {i}: shape {t.shape}, tensor[{label}]")
        # Sample operation: Cartesian product for 1D tensors
        if len(tensors) >= 1:
            prod = torch.cartesian_prod(*tensors)
            if prod.ndim > self.tensor_store.dimensionality_manager.get_current_dim():
                self.concepts.append(prod)  # Store in concepts (no ndim limit)
                print(f"  Cartesian product (concept, dim {prod.ndim}): {prod}")
            else:
                self.tensor_store.process(prod)
                print(f"  Cartesian product: {prod}")

if __name__ == "__main__":
    universe = Universe()
    consciousness = Consciousness()
    for _ in range(1):
        consciousness.observe()
    print(consciousness)
