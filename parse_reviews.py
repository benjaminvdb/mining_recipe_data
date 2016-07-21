#!/usr/bin/env python

import os
import glob
import argparse
import multiprocessing
import functools

from tqdm import tqdm
from bs4 import BeautifulSoup

from toolbox.argparse.actions import readable_dir, writable_file


def parse_file(filename, skip_missing=True):
    """
    Parse a HTML file containing an unparsed list of reviews.
    """
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse reviews from HTML')
    parser.add_argument('input', action=readable_dir, help='input directory with reviews')
    parser.add_argument('output', action=writable_file, help='output TSV file')
    parser.add_argument('--no-skip-missing', dest='skip_missing', action='store_false', help='skip review if there are missing values')
    parser.add_argument('--pool-size', type=int, default=multiprocessing.cpu_count(), help='number of processors to use')
    parser.set_defaults(skip_missing=True)

    args = parser.parse_args()

    # Get all filenames from the given path
    filenames = glob.glob(os.path.join(args.input, '*.html'))
    num_files = len(filenames)

    # Set up a pool of the required size
    p = multiprocessing.Pool(args.pool_size)

    # Construct the worker function, fixing the skip_missing argument
    func = functools.partial(parse_file, skip_missing=args.skip_missing)

    # Each worker process receives an unparsed review to process
    reviews = []
    for review in tqdm(p.imap_unordered(func, filenames), total=num_files):
        reviews.extend(review)

    with open(args.output, 'w') as fp:
        for review in reviews:
            fp.write('\t'.join(review))
            fp.write('\n')
