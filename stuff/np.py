import numpy as np
test = np.array([2])
test_ref = test
test_ref[0] = 3
my_vector = np.array([1, 2, 3, 4])
my_subset = my_vector[1:3]
my_subset[0] = -1
print(test)