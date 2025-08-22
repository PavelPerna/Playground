import torch

class Entity(object):
    def __init__(self):
        self.data = torch.Tensor([])


class EventListener(Entity):
    def __init__(self):
        self.events = torch.Tensor([True,False])

class Universe(Entity):
    pass
        

class Experience(Entity):
    pass

class Memory(Entity):
    
    def __getLink(self, exp : Experience) -> bool:
        link = self.__hash(exp)
        return link
    
    def __hash(exp):
        return exp
        
    
    def __isKnown(self, exp, link = False) -> bool:
        link = self.__getLink(exp)
        return link in self.data
    
    def process(self, exp:Experience) -> None:
        link = False
        if not self.__isKnown(exp, link):
            self.data[link] = exp

        
class Consciousness(Entity):
    def __init__(self):        
        self.memory = Memory()

    def __percieve(self) -> Experience | None:
        for exp in self.__analyzeInput(universe):
            self.memory.process(exp)
            return exp
        return None
    
    def __conceptualize(self):
        prod = torch.dot(torch.Tensor(self.memory),torch.Tensor(self.memory))
        print(prod)
        return False
    
    def __analyzeInput(self, universe):
        universe.observe(self)
            


        


universe = Universe()     
consciousness = Consciousness()
