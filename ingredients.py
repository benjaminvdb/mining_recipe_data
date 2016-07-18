import os
import re
import itertools
from collections import defaultdict

import numpy as np

from toolbox.strings import remove_range
from toolbox.io import UnicodeDictReader
from toolbox.functions import compose


def ingredient_iterator(directory):
    directory = os.path.abspath(os.path.expanduser(directory))
    for root, dirs, files in os.walk(directory):
        for f in files:
            f = os.path.join(root, f)
            data = np.load(f)['arr_0'][()]
            ingredients = data['ingredients']
            for ingredient in ingredients:
                yield ingredient


class StandardizedIngredients(object):
    """
    Lists the standardized ingredients of FooDB.
    """

    aliases = re.compile(r'(\(.*?\))')

    def __init__(self, filename):
        # One-to-one
        self._id_maps_details = defaultdict(list)

        # Many-to-one
        self._ingredient_maps_id = {}

        with open(filename) as fp:
            reader = UnicodeDictReader(fp, encoding='Windows-1252')

            for details in reader:
                if not details or not details['id'].isdigit():
                    continue
                name = details['name']

                scanner = self.aliases.scanner(name)
                m = scanner.search()

                if m: # Has alias(es)
                    aliases = m.group(1)[1:-1].split(',')
                    common_name = remove_range(name, m.start(), m.end())
                    aliases.append(common_name)
                else:  # Has no aliases
                    aliases = [name]

                clean = compose(unicode.lower, unicode.strip)

                # Map each alias to an id (many-to-one)
                for alias in itertools.imap(clean, aliases):
                    # NOTE: this is a VERY LAZY fix. There are multiple
                    # ingredients with (almost) the same name and we're just
                    # storing the first one that pops up (for now).
                    if alias in self._ingredient_maps_id:
                        continue

                    # This assertion fails!
                    #assert alias not in self._ingredient_maps_id, "Ingredient %s already in mapping" % alias
                    self._ingredient_maps_id[alias] = details['id']

                # Map each id to the corresponding details
                self._id_maps_details[id] = details

    def ingredients(self):
        """
        Returns ingredients and aliasses, making no distiction between the two.
        """
        return self._ingredient_maps_id.keys()

    def __getitem__(self, name):
        if isinstance(name, str) or isinstance(name, unicode):
            id_ = self._ingredient_maps_id[name]
            return self._id_maps_details[id_]
        elif isinstance(name, int):
            return self._id_maps_details[name]
        else:
            return None
