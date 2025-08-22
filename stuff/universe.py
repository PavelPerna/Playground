import torch


class Data(torch.Tensor):
    pass
       
    

class DataBase(object):
    def __init__(self, data = torch.Tensor([False])):
        self.__data = data
        self._ids = {}
    
    def process(self, data: Data):
        if hasattr(self.__data,'__iter__'):
            if not data in self.__data:
                self.__data.append(data)

    def state(self):
        if hasattr(self.__data,'__iter__'):
            return list(self.__data)
        return [self.__data]
    
    def __len__(self):
        return len(self.__data)-1
        
    def __getitem__(self, key): 
        return self.get(key)
    
    def __iter__(self):
        return iter(self.__data)
    
    def __repr__(self):
        res = "["
        for item in self.__data:
            res+= (f"{item}:{str(item)},")
        res +="]"
        return res
        
    
class Event(object):
    EVENT_NOOP = False
    EVENT_OBSERVE = True
    _EVENTS = [EVENT_NOOP,EVENT_OBSERVE]

    @classmethod
    def getEventList(self):
        return self._EVENTS

    
class EventListener(object):
    def __init__(self):
        self.database = DataBase()

class Entity(object):
    def __init__(self, data :list[torch.Tensor] = [torch.Tensor([False])]):
        self.database = DataBase(data)

    def reaction(self, event_id : bool = Event.EVENT_OBSERVE, actors = None, inputs = None):
        match event_id:
            case Event.EVENT_OBSERVE:
                return self.database.state()
        

    
class Potencial(Entity):
    def __init__(self, data = [], energy : bool = True):
        super.__init__(data)
        self.__energy = energy


class Universe(Entity):
    pass
    
        
class Consciousness(Entity):
    def __init__(self):
        super(Consciousness, self).__init__(Tensor([bool(self)]))

    def observe(self) -> Data:
        data = self.__actionObserve()
        for item in data:
            self.database.process(item)
        self.__conceptualize()
        return data
       
    def __conceptualize(self, new = None):
        knowledge = self.database.state()
        if not new:
            news = knowledge
        else:
            news = [torch.Tensor([new])]

        for new in news:
            print(f"Conceptualizing new : {new}")
            for known in knowledge:
                if torch.equal(known,new): 
                    continue 
                print(f"with known: {known}")
                product = torch.cartesian_prod(known,new)
                self.database.process(product)
                print(f"Product:{product}")
        
        
    
    def __actionObserve(self):
        return Action(action_id = Event.EVENT_OBSERVE).perform([self])

            

class Action(Entity):
    def __init__(self, action_id : int = Event.EVENT_OBSERVE):
        self.id = action_id
        pass

    def perform(self, actors : list[Consciousness] , inputs : list = None):
        observation = []
        observation.append(universe.reaction(event_id = self.id,actors = actors, inputs = inputs))
        for actor in actors:
            observation.append(actor.reaction(event_id = Event.EVENT_OBSERVE,actors = actors, inputs = inputs))
        return observation


        

if __name__ == "__main__":
    universe = Universe()     
    consciousness = Consciousness()
    i = 0
    while i < 2:
        i+=1
        consciousness.observe()
