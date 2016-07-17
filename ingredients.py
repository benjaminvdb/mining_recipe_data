import os

import numpy as np

def ingredient_iterator(directory):
    directory = os.path.abspath(os.path.expanduser(directory))
    print(directory)
    for root, dirs, files in os.walk(directory):
        print('Walking ' + root)
        for f in files:
            print("Processing " + f)
            f = os.path.join(root, f)
            data = np.load(f)['arr_0'][()]
            ingredients = data['ingredients']
            for ingredient in ingredients:
                yield ingredient['name']
