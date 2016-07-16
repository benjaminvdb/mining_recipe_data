#!/usr/bin/env python

import numpy as np

from toolbox.path import folder_apply

def get_ingredients(filename):
    data = np.load(filename)['arr_0'][()]
    return data['ingredients']

ingredients = folder_apply(get_ingredients, '~/00')
