class Test:
    def __init__(self, v = 0, t : type = int):
        self.type = t
        self.v = v

    def __get__(self, instance, owner):
        return self.type(self.v)
    def __set__(self, instance, value):
        self.v = value
        self.type = type(value)
    def __str__(self):
        return f"{str(self.type)}:{self.__get__(self,self)}"
    def __assign__(self, v):
        self.__set__(self.v,v)

class Picka(object):
    pass    
t = Test()
print(t)
t.__set__(t,"Pica")
print(t)
t.__set__(t,(0,1,(2,3)))
print(t)
t= 34
print(t)
