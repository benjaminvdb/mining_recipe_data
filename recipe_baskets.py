#!/usr/bin/env python

import argparse

import numpy as np
from tqdm import tqdm

from toolbox.argparse.actions import readable_dir, readable_file, writable_file

from recipe import get_recipes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Figure out the normalized ingredients from AllRecipes')
    parser.add_argument('recipes', action=readable_dir, help='input directory with recipes')
    parser.add_argument('mapping', action=readable_file, help='input file holding the mapping')
    parser.add_argument('basket', action=writable_file, help='output basket file')

    args = parser.parse_args()

    recipes = get_recipes(args.recipes)

    print("Loading mapper...")
    mapper = dict(filter(lambda x: x is not None, np.load(args.mapping)['arr_0'][()]))
    print("Finished loading mapper.")

    with open(args.basket, 'w') as fp:
        for recipe in tqdm(recipes):
            itemset = []
            for ingredient in recipe['ingredients']:
                id_ = ingredient['id']
                if id_ in mapper:
                    itemset.append(mapper[id_])
            fp.write(', '.join(itemset) + '\n')
