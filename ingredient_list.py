#!/usr/bin/env python

"""
Author:      Benjamin van der Burgh <benjaminvdb@gmail.com>
Date:        July 16th 2016
Description: Reconstructs the ingredient list, based on the ingredients of each
             recipe in the Ahn dataset. Replaces underscores with whitespaces.
"""

import csv
from itertools import ifilter

import numpy as np

ingredients = set()
with open('data/srep00196-s3.csv') as fp:
    # Instantiate a reader that skips comments
    reader = csv.reader(ifilter(lambda row: row[0] != '#', fp))

    # Iterate over all rows, storing each ingredient
    for row in reader:
        for ingredient in row[1:]:  # Skip the cuisine (item 0)
            ingredients.add(ingredient.replace('_', ' '))

np.savez_compressed('data/ingredient_list', ingredients)
