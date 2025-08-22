from typing import Generic, TypeVar


class _Undefined(type):
    def __instancecheck__(self, obj):
        if self is Base:
            raise TypeError("typing._Undefined cannot be used with isinstance()")
        return super().__instancecheck__(obj)

    def __repr__(self):
        if self is Base:
            return "typing._Undefined"
        return super().__repr__()  # respect to subclasses

    """
A base class for all entities in the system.
This class should not be instantiated directly. Instead, use subclasses that represent specific entities.
    """
class Undefined(metaclass=_Undefined):
    def __new__(cls, *args, **kwargs):
        if cls is Entity:
            raise TypeError("Undefined cannot be instantiated")
        return super().__new__(cls)

class Defined(Undefined):

    def __str__(self, raw: bool = True) -> str:
        r = f"{type(self)}: {self.__class__.__name__}\n"
        for attr, value in self.__dict__.items():
            value_str = repr(value) if raw else f"\n[\n{str(value)}\n]\n"
            r += f"\t - {attr}: {value_str}\n"
        return r.strip()
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __repr__(self) -> int:
        return 0
    
class Container(Entity,Generic[TOrigin]):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items = []

    def add_item(self, item: TOrigin):
        self._items.append(item)

    def get_items(self):
        return self._items

    def __str__(self) -> str:
        return f"Container with items: {self._items}"
    
class Universe(Container[Origin])