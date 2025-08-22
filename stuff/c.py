from typing import TypeVar, Generic
# Genesis 1:1 ( create identity for abstraction )
EARTH = TypeVar("Earth",default=None)
HEAVEN = TypeVar("Earth",default=tuple[EARTH])

class Earth(Generic[EARTH]):...

class Heaven(Generic[EARTH]):
    def __init__[EARTH](self, *args : EARTH):
        self.__dict__ = dict(args[1:])

e = EARTH
h = Heaven(e)

print(e,h)