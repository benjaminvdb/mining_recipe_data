#!/usr/bin/env python

import argparse

import numpy as np
from tqdm import tqdm

from toolbox.argparse.types import PathType

from recipe import get_recipes


if __name__ == '__main__':
    input_type = PathType(exists=True, type='dir')
    output_type = argparse.FileType('w')

    parser = argparse.ArgumentParser(description='Figure out the normalized ingredients from AllRecipes')
    parser.add_argument('recipes', type=input_type, help='input directory')
    parser.add_argument('basket', type=output_type, help='output file')

    args = parser.parse_args()

    recipes = get_recipes(args.recipes)

    print("Loading mapper...")
    mapper = dict(filter(lambda x: x is not None, np.load('ingredient_mappings.npz')['arr_0'][()]))
    print("Finished loading mapper.")

    with open(args.output, 'w') as fp:
        for recipe in tqdm(recipes):
            itemset = []
            for ingredient in recipe['ingredients']:
                id_ = ingredient['id']
                if id_ in mapper:
                    itemset.append(mapper[id_])
            fp.write(', '.join(itemset) + '\n')
