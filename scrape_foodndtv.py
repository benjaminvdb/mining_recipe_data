#!/usr/bin/env python

import urllib2
import re

from bs4 import BeautifulSoup


def char_range(c1, c2, lower=False):
    """Generates the characters from `c1` to `c2`, inclusive."""
    for c in xrange(ord(c1), ord(c2)+1):
	if lower:
	    yield chr(c).lower()
	else:
	    yield chr(c)


def get_category_urls(base_url):
    html = urllib2.urlopen(base_url).read()

    soup = BeautifulSoup(html, 'html5lib')

    # Gather the category URLs
    categories = soup.find_all('a', href=re.compile(r'http://food.ndtv.com/ingredient/\w+'))
    urls = list(set(map(lambda x: x['href'], categories)))

    return urls


def urljoin(first, second):
    return '/'.join([first, second])


def scraper(urls):
    all_ingredients = []
    for url in urls:
        for ch in char_range('a', 'z', lower=True):
            current = urljoin(url, ch)
            print("Currently parsing URL: %s" % current)

            html = urllib2.urlopen(current).read()
            soup = BeautifulSoup(html, 'html5lib')

            container = soup.find('div', class_='vdo_lst')
            links = container.find_all(lambda tag: tag.name == 'a' and tag.has_attr('title'))
            ingredients = list(set(map(lambda tag: tag['title'], links)))

            print("Adding %d new ingredients" % len(ingredients))

            all_ingredients.extend(ingredients)
    return all_ingredients


if __name__ == '__main__':
    base_url = 'http://food.ndtv.com/ingredient'
    urls = get_category_urls(base_url)
    ingredients = scraper(urls)
