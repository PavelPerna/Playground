
from derive import ParentClass
from child_class1 import ChildClass1


class ChildClass3(ChildClass1):
    def __init__(self):
        super().__init__()
        self.version = 3
    
    def child_class3_method(self):
        print('Child class 3 method')
