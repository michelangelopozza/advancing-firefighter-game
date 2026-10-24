import numpy as np

vals = np.column_stack((
        np.random.uniform(0, 10, 10),
        np.random.uniform(0, 10, 10)
    ))

keys = np.zeros(10).astype(int)
for i in range(10):
    keys[i] = i

e = zip(keys, vals)
d = dict(e)
print(d)