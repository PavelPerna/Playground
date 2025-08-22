
from derive import ParentClass


class ChildClass1(ParentClass):
    def __init__(self):
        super().__init__()
        self.version = 1
    
    def child_class1_method(self):
        print('Child class 1 method')
