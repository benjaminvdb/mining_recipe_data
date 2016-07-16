#!/usr/bin/env python

import os
import itertools
import argparse
from collections import defaultdict
from HTMLParser import HTMLParser

import numpy as np
import inflection

from toolbox.strings import long_substr


def aggregate_ingredients(directory):
    h = HTMLParser()

    ingredients = defaultdict(list)

    # Walk directory recursively and create, per ingredient, a list of textual
    # occurrences as it appeared on the website.
    for root, dirnames, filenames in os.walk(directory):
        # Root can be relative, so convert to absolute path and join with filename
        filenames = map(lambda filename: os.path.join(os.path.abspath(root), filename), filenames)

        # Loop over all files and create a dictionary of id -> ['list', 'of', 'occurrences']
        for filename in itertools.ifilter(os.path.isfile, filenames):
            data = np.load(filename)['arr_0'][()]
            for ingredient in data['ingredients']:
                # NOTE: Text contains HTML escaped text, e.g. 'jalape&#241;o', so unescape this
                ingredients[ingredient['id']].append(h.unescape(ingredient['name']))

    return ingredients


def core_ingredients(ingredients):
    """
    # 1) Find the longest common substring (removes stuff like '1/2 tablespoon ..')
    # 2) Singularize the ingredient (caraway seeds -> caraway seed)
    # 3) Clean up the string by removing whitespace
    """
    return {key: inflection.singularize(long_substr(value).strip()) for key, value in ingredients.iteritems()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Aggregate ingredients')
    parser.add_argument('input', type=str, help='input directory')
    parser.add_argument('output', type=str, help='output file')
#    parser.add_argument('--pool-size', '-p', type=int, help='pool size (= number of workers)')
#    parser.add_argument('--chunk-size', '-c', type=int, default=1, help='chunk size (= worker batch size)')

    args = parser.parse_args()

    ingredients = aggregate_ingredients(args.input)
    ingredients2 = core_ingredients(ingredients)

    np.savez_compressed(args.output, ingredients2)
