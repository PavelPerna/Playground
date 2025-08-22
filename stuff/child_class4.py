
from derive import ParentClass
from child_class1 import ChildClass1
from child_class2 import ChildClass2


class ChildClass4(ChildClass2):
    def __init__(self):
        super().__init__()
        self.version = 4
    
    def child_class4_method(self):
        print('Child class 4 method')
