#!/usr/bin/env python

import os
import glob
import argparse
import multiprocessing
import functools
import codecs
import json
from HTMLParser import HTMLParser

from tqdm import tqdm
from bs4 import BeautifulSoup

from toolbox.argparse.actions import readable_dir, writable_file
from toolbox.io import UnicodeWriter


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
    parser.add_argument('--delimiter', '-d', type=unicode, default=',', help='the separator to use in the output file')
    parser.set_defaults(skip_missing=True)

    args = parser.parse_args()

    # Get all filenames from the given path
    filenames = glob.glob(os.path.join(args.input, '*.html'))

    # Set up a pool of the required size
    p = multiprocessing.Pool(args.pool_size)

    # Construct the worker function, fixing the skip_missing argument
    func = functools.partial(parse_file, skip_missing=args.skip_missing, remove=args.delimiter)

    # Each worker process receives an unparsed review to process
    reviews = []
    name_to_userid = {}
    print('Parsing HTML files...')
    for res_reviews in tqdm(p.imap_unordered(func, filenames), total=len(filenames)):

        # Replace name with user_id
        for id_, author, rating, date in res_reviews:
            if author in name_to_userid:  # Known author, map to userid
                author = name_to_userid[author]
            else:  # Unknown author, assign a userid
                userid = len(name_to_userid)
                name_to_userid[author] = userid
                author = userid
            reviews.append((id_, author, rating, date))
    print('Finished parsing files.')

    print('Saving %d reviews to file...' % len(reviews))
    with codecs.open(args.output, 'w') as fp:
        writer = UnicodeWriter(fp, encoding='utf-8')
        writer.writerows(reviews)
    print('Finished saving reviews.')

    userid_to_name = {userid: name for name, userid in name_to_userid.items()}  # Invert map
    print('Saving %d id -> username mapping to file...' % len(userid_to_name))
    with codecs.open(args.map, 'w') as fp:
        json.dump(userid_to_name, fp, ensure_ascii=False, indent=2)
    print('Finished saving user mappings.')

    print('Finished!')
