#!/usr/bin/env python

import argparse
import functools
import multiprocessing
import re
from collections import defaultdict
from HTMLParser import HTMLParser

from ingreedypy import Ingreedy
from parsimonious import IncompleteParseError
import numpy as np

from ingredients import get_ingredients, StandardizedIngredients
from toolbox.strings import remove_word
from toolbox.functions import compose

mapper = defaultdict(list)


def victory_parser(s):
    """
    Fuck you, strings that are not accounted for Ingreedy's grammar.

    NOTE: simply removes words (= consecutive characters separated from other
    words with `sep`) if a specific character cannot be parsed.
    """
    parser = Ingreedy()
    while True:
        try:
            parsed = parser.parse(s)
            return parsed['ingredient']
        except IncompleteParseError as err:
            column = err.column()

            # If Ingreedy errors in a whitespace, skip back to last word before
            # sending the column to remove_word.
            while s[column] == ' ':
                column = column -1
            s = remove_word(s, column)


def clean_ingredient(s):
    """
    Remove common garbage from ingredient, such as brand names and quotes info.
    """
    return re.sub(r"(?:\(.*?\) |'.*?' |(([0-9A-Z]\w+\s*)+\xae) )", '', s)


def html_unescape(s):
    """
    Turns escaped HTML into unicode.
    """
    parser = HTMLParser()
    return parser.unescape(s)


def process(ingredient, std):
    # Create pipeline of cleaning steps and apply to ingredient name
    normalize = compose(victory_parser, html_unescape, unicode.lower, clean_ingredient)
    name = normalize(ingredient['name'])

    for s in std:
        matches = True
        for el in s:
            if el not in name:
                matches = False
                break
        if matches:
            return (ingredient['id'], ' '.join(s))


def wrapper(ingredient, std=None):
    """
    Wrapper ensures that errors are ignored and the error is just printed to
    the console, allowing the processing to continue.
    """
    try:
        return process(ingredient, std)
    except Exception as err:
        print("Couldn't process {0}: {1}".format(ingredient, err))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Figure out the normalized ingredients from AllRecipes')
    parser.add_argument('ingredients', type=str, help='input directory')
    parser.add_argument('std', type=str, help='standardized ingredients')
    parser.add_argument('output', type=str, help='output file')

    args = parser.parse_args()

    p = multiprocessing.Pool()#args.pool_size)

    print("Loading standardized ingredients...")
    std = map(unicode.split, StandardizedIngredients(args.std).ingredients())
    print("Done loading %d standardized ingredients." % len(std))

    func = functools.partial(wrapper, std=std)

    print("Loading recipes...")
    ingredients = get_ingredients(args.ingredients)
    print("Done loading %d recipes." % len(ingredients))

    r = p.map_async(func, ingredients)
    r.wait()

    np.savez_compressed(args.output, r.get())
