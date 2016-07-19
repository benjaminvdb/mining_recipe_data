import numpy as np

from toolbox.path import folder_apply


def load_recipe(filename):
    return np.load(filename)['arr_0'][()]


def get_recipes(directory, ignore=None):
    recipes = folder_apply(load_recipe, directory)
    return filter(lambda recipe: recipe['name'] != u'Johnsonville\xae Three Cheese Italian Style Chicken Sausage Skillet Pizza', recipes)
