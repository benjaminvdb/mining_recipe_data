#!/usr/bin/env python

import os
import glob
import argparse

from tqdm import tqdm
from bs4 import BeautifulSoup

from toolbox.argparse.actions import readable_dir, writable_file


reviews = []

def parse_file(filename):
    reviews = []
    with open(filename) as fp:
        soup = BeautifulSoup(fp, 'html5lib')

        for review in soup(attrs={'itemprop': 'review'}):
            id_ = os.path.splitext(os.path.basename(filename))[0]
            author = review.find(attrs={'itemprop': 'author'}).text.strip()
            rating = review.find(attrs={'itemprop': 'ratingValue'})['content']
            date = review.find(attrs={'itemprop': 'dateCreated'})['content']

            reviews.append((id_, author, rating, date))
    return reviews


def save_file(filename):
    with open(filename, 'w') as fp:
        for review in reviews:
            fp.write('\t'.join(review))
            fp.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse reviews from HTML')
    parser.add_argument('input', action=readable_dir, help='input directory with reviews')
    parser.add_argument('output', action=writable_file, help='output TSV file')

    args = parser.parse_args()

    filenames = glob.glob(os.path.join(args.input, '*.html'))

    reviews = []
    for filename in tqdm(filenames):
        reviews.extend(parse_file(filename))

    save_file(args.output)
