#!/usr/bin/env python

import argparse
import multiprocessing

import numpy as np
from tqdm import tqdm
import glob2

from toolbox.argparse.actions import readable_dir, readable_file, writable_file
from toolbox.path import expand


def load_recipe(filename):
    return np.load(filename)['arr_0'][()]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Figure out the normalized ingredients from AllRecipes')
    parser.add_argument('recipes', action=readable_dir, help='input directory with recipes')
    parser.add_argument('mapping', action=readable_file, help='input file holding the mapping')
    parser.add_argument('single', action=writable_file, help='output basket file')
    parser.add_argument('--pool-size', '-p', default=multiprocessing.cpu_count(), help='pool size (= number of workers)')

    args = parser.parse_args()

    p = multiprocessing.Pool(args.pool_size)

    directory = expand(args.recipes)

    print("Loading recipes...")
    recipes = []
    for recipe in tqdm(p.imap_unordered(glob2.iglob(directory + '/**/*'))):
        if recipe:
            recipes.append(recipe)

    print("Finished loading %d recipes." % len(recipes))

    print("Loading mapper...")
    mapper = dict(recipes)
    print("Finished loading mapper with %d keys." % len(mapper.keys()))

    print("Computing recipe itemsets and saving to file...")
    with open(args.basket, 'w') as fp:
        for recipe in tqdm(recipes):
            itemset = set()
            for ingredient in recipe['ingredients']:
                id_ = ingredient['id']
                if id_ in mapper:
                    itemset.add(mapper[id_])

            for item in itemset:
                fp.write(str(recipe['id']) + ',' + item + '\n')
    print("Finished!")
