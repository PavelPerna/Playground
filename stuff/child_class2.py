
from derive import ParentClass


class ChildClass2(ParentClass):
    def __init__(self):
        super().__init__()
        self.version = 2
    
    def child_class2_method(self):
        print('Child class 2 method')
