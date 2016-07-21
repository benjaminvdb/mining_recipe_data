#!/usr/bin/env python

import os
import glob
import argparse
import multiprocessing

from tqdm import tqdm
from bs4 import BeautifulSoup

from toolbox.argparse.actions import readable_dir, writable_file


reviews = []

def parse_file(filename, skip_missing=True):
    reviews = []
    with open(filename) as fp:
        soup = BeautifulSoup(fp, 'html5lib')

        for review in soup(attrs={'itemprop': 'review'}):
            id_ = os.path.splitext(os.path.basename(filename))[0]

            author_el = review.find(attrs={'itemprop': 'author'})
            rating_el = review.find(attrs={'itemprop': 'ratingValue'})
            date_el = review.find(attrs={'itemprop': 'dateCreated'})

            # Review is complete or we're fine using None as missing value
            if (author_el and rating_el and date_el) or not skip_missing:
                author = author_el.text.strip() if author_el else None
                rating = rating_el['content'] if rating_el else None
                date = date_el['content'] if date_el else None
            else:  # Otherwise, we just skip the review
                continue

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
    parser.add_argument('--skip-missing', action='store_true', help='skip review if there are missing values')
    parser.add_argument('--pool-size', default=multiprocessing.cpu_count(), help='number of processors to use')

    args = parser.parse_args()

    filenames = glob.glob(os.path.join(args.input, '*.html'))

    p = multiprocessing.Pool(args.pool_size)

    reviews = []
    for review in tqdm(p.imap_unordered(parse_file, filenames)):
        reviews.extend(review)

    save_file(args.output)
