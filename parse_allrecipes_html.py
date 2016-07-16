from __future__ import division
import re
import datetime
import json
import glob
import os
import multiprocessing
import argparse
import hashlib
import random

from bs4 import BeautifulSoup
from pyparsing import Optional, Group, Word, nums, Literal
from tqdm import tqdm
import numpy as np

from toolbox.strings import pad_left


def autoconvert(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

class ExtendedEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.timedelta):
            # NOTE: uses default string representation, e.g. "00:30:00"
            return str(obj)
        return json.JSONEncoder.default(self, obj)

# Integer numbers
number = Word(nums)

# Optional hour part
hour_symbol = Literal('h')
hour = Group(number + hour_symbol)('hour').setParseAction(lambda s,l,t: int(t[0][0][0]))

# Optional minute part
minute_symbol = Literal('m')
minute = Group(number + minute_symbol)('minute').setParseAction(lambda s,l,t: int(t[0][0]))

# Put the hours and minutes together
duration = Optional(hour) + Optional(minute)

# Convert resulting dictionaries into datetime.timedelta
def timedict_to_timedelta(d):
    hours = d['hour'] if 'hour' in d else 0
    minutes = d['minute'] if 'minute' in d else 0
    return datetime.timedelta(hours=hours, minutes=minutes)

# Put everything together: parse string and output a timedelta
duration_parser = lambda s: timedict_to_timedelta(duration.parseString(s).asDict())


def dict_to_string(d):
    return ''.join([str(value) for value in d.itervalues()])


def hash_dict(d):
    return hashlib.md5(dict_to_string(d)).hexdigest()


def parse_ingredients(li):
    ingredients = []
    for el in li:
        label = el.find('label', attrs={'ng-class': "{true: 'checkList__item'}[true]"})
        if label:
            span = label.find('span')

            ingredient = dict()
            ingredient['id'] = int(span['data-id'])
            ingredient['name'] = span.text

            ingredients.append(ingredient)
    return ingredients


def parse_file(filename):
    fp = open(filename)
    soup = BeautifulSoup(fp, 'html5lib', convertEntities=BeautifulSoup.HTML_ENTITIES)

    # Get ID from filename
    basename = os.path.basename(filename)
    id_ = os.path.splitext(basename)[0]
    recipe = {'id': int(id_)}

    name = soup.find('h1', itemprop='name').text
    recipe['name'] = name

    ingredients = []
    li = soup.find('ul', id="lst_ingredients_1")('li')
    ingredients = parse_ingredients(li)

    li = soup.find('ul', id='lst_ingredients_2')('li')
    ingredients2 = parse_ingredients(li)
    ingredients.extend(ingredients2)
    recipe['ingredients'] = ingredients

    yield_ = soup.find('meta', itemprop='recipeYield')
    recipe['yields'] = int(yield_['content']) if yield_ is not None else None

    cal = soup.find('span', class_='calorie-count')
    recipe['calories'] = int(cal.find('span').text) if cal is not None else None

    nut = soup.find('h3', text='Nutrition')
    nutrients = dict()
    if nut:
        for ul in nut.find_next_siblings(class_='nutrientLine'):
            try:
                nutrient_type = ul.find('li').text.rstrip(': ')
                amount = ul.find('li', class_='nutrientLine__item--amount')
                nutrients[nutrient_type] = autoconvert(amount.find('span').text)
            except:
                continue
    recipe['nutrients'] = nutrients if nutrients else None

    prep = soup.find('span', class_='ready-in-time')
    recipe['preparation_time'] = duration_parser(prep.text) if prep else None

    prep_root = soup.find('ul', class_='prepTime')
    if prep_root:  # Has time information
        preptime = prep_root.find('time', itemprop='prepTime')
        recipe['preparation_time'] = duration_parser(preptime.text).seconds if preptime else None

        cooktime = prep_root.find('time', itemprop='cookTime')
        recipe['cooking_time'] = duration_parser(cooktime.text).seconds if cooktime else None

        totaltime = prep_root.find('time', itemprop='totalTime')
        recipe['total_time'] = duration_parser(totaltime.text).seconds if totaltime else None

    start_number = re.compile(r'(\d+).*?')

    try:
        rating_stars = soup.find('section', id='reviews').find('ol').find_all('li')
        assert len(rating_stars) == 6, "Expected 5 degrees of ratings and a total count, for a total of 6, but got %d" % len(rating_stars)
        recipe['rating_count'] = int(rating_stars.pop(0).text.rstrip(' Ratings'))
        ratings = dict()
        for idx, degree in enumerate(rating_stars):
            stars_title = degree.div['title']
            number_of_stars = str(5 - idx)
            ratings[number_of_stars + ' stars'] = int(start_number.match(stars_title).group(1))
        recipe['ratings'] = ratings
    except Exception:
        pass

    directory = random_dir(args.output)

    np.savez_compressed(os.path.join(directory, str(recipe['id'])), recipe)


def split_list(l, n):
    """
    Split list into n smaller lists, not preserving ordering.
    """
    res = [[] for i in xrange(n)]
    x = 0
    while x < len(l):
        for sublist_idx in xrange(n):
            if x == len(l):
                break
            res[sublist_idx].append(l[x])
            x = x + 1
    return res


def wrapper(filename):
    try:
        parse_file(filename)
    except Exception as err:
        print('Error parsing {0}: {1}'.format(filename, err))


def random_dir(root):
    dirsize = 469
    strlen = len(str(dirsize))

    rand1 = random.randint(0, dirsize)  # Using sqrt(number_files)
    dir1 = pad_left(str(rand1), '0', strlen)

    rand2 = random.randint(0, dirsize)
    dir2 = pad_left(str(rand2), '0', strlen)

    level1 = os.path.join(os.path.abspath(root), dir1)
    level2 = os.path.join(level1, dir2)

    if not os.path.exists(level1):
        os.makedirs(level1)

    if not os.path.exists(level2):
        os.makedirs(level2)

    return level2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process recipe files')
    parser.add_argument('input', type=str, help='input directory')
    parser.add_argument('output', type=str, help='output file')
    parser.add_argument('--pool-size', '-p', type=int, help='pool size (= number of workers)')
    parser.add_argument('--chunk-size', '-c', type=int, default=1, help='chunk size (= worker batch size)')

    args = parser.parse_args()

    recipes = []

    p = multiprocessing.Pool(args.pool_size)

    # Parse all HTML files in target folder
    filenames = glob.glob(args.input + '/*.html')
    print("Got %d files." % len(filenames))

    for result in tqdm(p.imap_unordered(wrapper, filenames, chunksize=args.chunk_size), total=len(filenames)):
        pass
#    p.map_async(parse_file, filenames)#, chunksize=args.chunk_size)
