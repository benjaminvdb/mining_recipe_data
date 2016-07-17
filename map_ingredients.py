#!/usr/bin/env python

import csv
import argparse
from collections import defaultdict

from tqdm import tqdm
from ingreedypy import Ingreedy
from parsimonious import IncompleteParseError

from ingredients import ingredient_iterator

mapper = defaultdict(list)


def remove_offending_word(s, col, sep=' '):
    """
    Remove the word that contains the letter at position `col` and use `sep` as
    word separators.
    """
    start = col
    stop = col

    # Look behind for start of word
    while s[start] != sep and start >= 0:
        start = start - 1

    # Look forward to end of word
    while s[stop] != sep and stop < len(s):
        stop = stop + 1

    # Eat the fucking word and send it to hell
    return s[:start] + s[stop:]


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
            s = remove_offending_word(s, err.column())


def process(ingredient, std):


def wrapper(args):
    try:
        process(args[0], args[1])
    except Exception as err:
        print("Couldn't process {0}: {1}".format(args[0], err))




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Figure out the normalized ingredients from AllRecipes')
    parser.add_argument('input', type=str, help='input directory')
    parser.add_argument('output', type=str, help='output file')

    args = parser.parse_args()

    std = None
    with open(args.input) as fp:
        reader = csv.DictReader(fp)
        std = [el['name'].lower().decode('Windows-1252').split(' ') for el in reader]

    for ingredient in tqdm(ingredient_iterator(args.input)):
        for s in std:
            matches = True
            for el in s:
                allrecipe_ingredient = victory_parser(ingredient['name'])
                if el not in allrecipe_ingredient:
                    matches = False
                    break
            if matches:
                mapper[ingredient['id']].append(' '.join(s))
                break
