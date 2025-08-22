
from derive import ParentClass
from child_class1 import ChildClass1
from child_class2 import ChildClass2
from child_class3 import ChildClass3


class ChildClass5(ChildClass3):
    def __init__(self):
        super().__init__()
        self.version = 5
    
    def child_class5_method(self):
        print('Child class 5 method')
