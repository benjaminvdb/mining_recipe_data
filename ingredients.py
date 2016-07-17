import os

import numpy as np

def ingredient_iterator(directory):
    directory = os.path.abspath(os.path.expanduser(directory))
    for root, dirs, files in os.walk(directory):
        for f in files:
            f = os.path.join(root, f)
            data = np.load(f)['arr_0'][()]
            ingredients = data['ingredients']
            for ingredient in ingredients:
                yield ingredient
