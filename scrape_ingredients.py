#!/usr/bin/env python

"""
Author:      Benjamin van der Burgh <benjaminvdb@gmail.com>
Date:        July 16th 2016
Description: Scrapes ingredients from USDA Branded Food Products Database.
"""

import re
import urllib2

import numpy as np
from tqdm import tqdm
from bs4 import BeautifulSoup

url = 'https://ndb.nal.usda.gov/ndb/foods?format=&count=&max=9999999&sort=&fgcd=&manu=&lfacet=&qlookup=&offset=0&order=desc'

data = urllib2.urlopen(url).read()

soup = BeautifulSoup(data, 'html5lib')

l = soup.find('div', class_='list-left')
table = l.find('tbody')

regex = re.compile(r'/ndb/foods/show/([0-9]+?)\?')  # Strips internal id

ingredients = []
rows = table.find_all('tr')
for row in tqdm(rows):
    ingredient = dict()

    data = map(lambda x: x.text.strip(), row.find_all('td'))

    ingredient['id'] = int(data[0])
    ingredient['description'] = data[1]
    ingredient['group'] = data[2]

    follow_url = row.find('a')['href']
    ingredient['url_id'] = regex.match(follow_url).group(1)

    ingredients.append(ingredient)

np.savez_compressed('ingredient_list', ingredients)
