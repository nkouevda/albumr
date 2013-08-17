#!/usr/bin/env python3

# Nikita Kouevda
# 2013/08/17

import os
import re
import sys
from argparse import ArgumentParser
from html.parser import HTMLParser
from multiprocessing import Pool
from urllib.request import urlopen


def save_image(url, path, verbose=False):
    if os.path.exists(path):
        print('error: file exists: ' + path, file=sys.stderr)
    else:
        try:
            with urlopen(url) as in_url:
                with open(path, 'wb') as out_file:
                    if verbose:
                        print('saving file: ' + path)

                    out_file.write(in_url.read())
        except:
            print('error: could not save file: ' + path, file=sys.stderr)


def save_albums(albums, numbers=False, titles=False, verbose=False):
    html_parser = HTMLParser()

    re_album_hash = re.compile(r'(?:.*/)?([A-Za-z0-9]{5})(?:[/#].*)?$')
    re_image = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
    re_title = re.compile(r'data-title="(.*?)"')
    re_title_sanitize = re.compile(r'(?:[^ -~]|[/:])+')

    # Use a process pool to save images in parallel
    pool = Pool()
    kwds = {'verbose': verbose}

    for album in albums:
        try:
            directory = album_hash = re_album_hash.match(album).group(1)

            with urlopen('http://imgur.com/a/' + album_hash) as in_url:
                content = in_url.read().decode()
        except:
            print('error: could not read album: ' + album, file=sys.stderr)
            continue

        if titles:
            title_raw = re_title.search(content).group(1)
            title_parsed = html_parser.unescape(title_raw)
            title_sanitized = re_title_sanitize.sub(' ', title_parsed)
            directory += '-[' + title_sanitized + ']'

        if not os.path.exists(directory):
            if verbose:
                print('making directory: ' + directory)

            os.makedirs(directory)

        for number, pair in enumerate(re_image.finditer(content)):
            filename = pair.group(1) + pair.group(2)
            url = 'http://i.imgur.com/' + filename

            if numbers:
                path = '{0}/{2}'.format(directory, filename)
            else:
                path = '{0}/{1}-{2}'.format(directory, number, filename)

            pool.apply_async(save_image, args=(url, path), kwds=kwds)

    # Wait for worker processes to complete
    pool.close()
    pool.join()


def main():
    parser = ArgumentParser(description='Download Imgur albums')

    parser.add_argument('albums', nargs='+', type=str, metavar='album',
                        help='an album hash or URL')
    parser.add_argument('-n', '--numbers', action='store_true',
                        help='prepend numbers to filenames')
    parser.add_argument('-t', '--titles', action='store_true',
                        help='append album titles to directory names')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose output')

    args = parser.parse_args()

    save_albums(args.albums, numbers=args.numbers, titles=args.titles,
                verbose=args.verbose)


if __name__ == '__main__':
    main()
