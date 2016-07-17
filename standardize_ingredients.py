#!/usr/bin/env python

import re
import argparse
import os

import numpy as np
import inflection
import ingreedypy


def convert_ingredients(ingredients):
    parser = ingreedypy.Ingreedy()
    parens = re.compile(r"(?:\(.*?\) |'.*?' |\d+% |\d+-inch |(([A-Z]\w+\s*)+\xae) )")

#    exclude = ['organic', 'medium']

    ws = re.compile(r'\s+')
    res = []
    for ingredient in ingredients:
        stored = ingredient
        try:
            ingredient = parens.sub('', ingredient)
            ingredient = ingredient.lower()
            ingredient = ws.sub(' ', ingredient).strip()
            ingredient = parser.parse(ingredient)['ingredient']
            ingredient = inflection.singularize(ingredient)
            res.append(ingredient)
        except Exception as err:
            print("Error for {0}: {1}".format(stored, err))
            break
    return res

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Normalize ingredients')
    parser.add_argument('input', type=str, help='input directory')
    parser.add_argument('output', type=str, help='output')
    parser.add_argument('--encoding', type=str, default='Windows-1252', help='output encoding')

    args = parser.parse_args()

    directory = os.path.abspath(os.path.expanduser(args.input))

    out = []

    for root, dirs, files in os.walk(directory):
        for f in files:
            f = os.path.join(root, f)
            old = [ingredient['name'] for ingredient in np.load(f)['arr_0'][()]['ingredients']]
            new = convert_ingredients(old)
            out.extend(zip(old, new))

    with open(args.output, 'w') as fp:
        fp.write('sep=\t\n')
        for row in out:
            fp.write('\t'.join(map(lambda x: x.encode(args.encoding), row)))
            fp.write('\n')
