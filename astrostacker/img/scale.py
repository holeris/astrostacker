import numpy as np


# Define a function for making a linear gray scale
def lingray(x, a=None, b=None, max=1.0):
    """
    Auxiliary function that specifies the linear gray scale.
    a and b are the cutoffs : if not specified, min and max are used
    """
    if a is None:
        a = np.min(x)
    if b is None:
        b = np.max(x)
    return max * (x - float(a)) / (b - a)