#!/usr/bin/env python

import os
import glob
import argparse
import multiprocessing
import functools
import codecs
import json
from HTMLParser import HTMLParser

import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup

from toolbox.argparse.actions import readable_dir, writable_file


def parse_file(filename, skip_missing=None, remove=None):
    """
    Parse a HTML file containing an unparsed list of reviews.
    """
    parser = HTMLParser()
    reviews = []
    with codecs.open(filename, encoding='utf-8') as fp:
        soup = BeautifulSoup(fp, 'html5lib')

        for review in soup(attrs={'itemprop': 'review'}):
            id_ = os.path.splitext(os.path.basename(filename))[0]

            author_el = review.find(attrs={'itemprop': 'author'})
            rating_el = review.find(attrs={'itemprop': 'ratingValue'})
            date_el = review.find(attrs={'itemprop': 'dateCreated'})

            # Review is complete or we're fine using None as missing value
            if (author_el and rating_el and date_el) or not skip_missing:
                author = parser.unescape(author_el.text.replace(remove, '').strip()) if author_el else None
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
    parser.add_argument('map', action=writable_file, help='output file for mapping in JSON')
    parser.add_argument('--no-skip-missing', dest='skip_missing', action='store_false', help='skip review if there are missing values')
    parser.add_argument('--pool-size', '-p', type=int, default=multiprocessing.cpu_count(), help='number of processors to use')
    parser.add_argument('--delimiter', '-d', type=str, default=',', help='the separator to use in the output file')
    parser.set_defaults(skip_missing=True)

    args = parser.parse_args()

    # Get all filenames from the given path
    filenames = glob.glob(os.path.join(args.input, '*.html'))
    num_files = len(filenames)

    # Set up a pool of the required size
    p = multiprocessing.Pool(args.pool_size)

    # Construct the worker function, fixing the skip_missing argument
    func = functools.partial(parse_file, skip_missing=args.skip_missing, remove=args.delimiter)

    # Each worker process receives an unparsed review to process
    reviews = []
    for review in tqdm(p.imap_unordered(func, filenames), total=num_files):
        reviews.extend(review)

    df = pd.DataFrame(reviews, columns=['id', 'user', 'rating', 'date'])
    df.set_index('id', inplace=True)

    # Create a hashmap for user
    usernames = df['user'].unique()
    num_users = len(usernames)
    ids = range(num_users)
    name_to_id = dict(zip(ids, usernames))
    id_to_name = dict(zip(usernames, ids))

    # Replace usernames
    df.replace({'user': id_to_name}, inplace=True)

    # Save reviews
    df.to_csv(args.output, encoding='utf-8', sep=args.delimiter)

    # Save the id -> username mapping
    with codecs.open(args.map, 'w', encoding='utf-8') as fp:
        json.dump(id_to_name, fp, ensure_ascii=False, indent=2)
