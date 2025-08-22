import os

# Base class
class ParentClass:
    def __init__(self):
        self.version = 0

    def derive(self):
        # Generate the next class name and method
        next_version = self.version + 1
        class_name = f"ChildClass{next_version}"
        method_name = f"child_class{next_version}_method"
        reimport = "from derive import ParentClass\n"
        parent_class = "ParentClass"
        for i in range(self.version):
            if i > 0:
                reimport += f"from child_class{i} import ChildClass{i}\n"
                parent_class = f"ChildClass{i}"
        # Create class definition as a string
        class_def = f"""
{reimport}

class {class_name}({parent_class}):
    def __init__(self):
        super().__init__()
        self.version = {next_version}
    
    def {method_name}(self):
        print('Child class {next_version} method')
"""
        return class_def, class_name

def save_class_def(class_def: str, filename: str):
    with open(filename, 'w') as f:
        f.write(class_def)

def load_class_def(filename: str):
    with open(filename, 'r') as f:
        return f.read()

def main():
    iterations = 5

    # Initialize with ParentClass
    current_class = ParentClass
    current_instance = current_class()
    print(f"Version {current_instance.version}")

    # Run the cycle
    for i in range(iterations):
        filename = f"child_class{current_instance.version + 1}.py"
        # Generate and save the descendant class
        class_def, class_name = current_instance.derive()
        save_class_def(class_def, filename)

        # Load and execute the class definition
        with open(filename, 'r') as f:
            exec(f.read(), globals())

        # Create an instance of the new class
        current_class = globals()[class_name]
        current_instance = current_class()
        print(f"Version {current_instance.version}")

        # Call the child-specific method
        method_name = f"child_class{current_instance.version}_method"
        if hasattr(current_instance, method_name):
            getattr(current_instance, method_name)()

        # Clean up the file for clarity (optional)
        #if i == iterations - 1:
        #    os.remove(filename)

if __name__ == "__main__":
    main()