import numpy as np

def load_recipe(filename):
    return np.load(filename)['arr_0'][()]
