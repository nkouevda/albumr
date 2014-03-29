#!/usr/bin/env python3

# Nikita Kouevda
# 2014/03/29

import os
import re
import sys
from argparse import ArgumentParser
from html.parser import HTMLParser
from multiprocessing import Pool
from urllib.request import urlopen


PROGRAM = os.path.basename(__file__)


def print_error(message):
    print(PROGRAM + ': ' + message, file=sys.stderr)


def save_image(url, path, verbose=False):
    if os.path.exists(path):
        print_error('file exists: ' + path)
        return

    try:
        with urlopen(url) as in_url:
            content = in_url.read()

        if verbose:
            print('saving file: ' + path)

        with open(path, 'wb') as out_file:
            out_file.write(content)
    except:
        print_error('could not save file: ' + path)


def save_albums(albums, numbers=False, titles=False, verbose=False):
    html_parser = HTMLParser()

    re_album_hash = re.compile(r'(?:.*/)?([A-Za-z0-9]{5})(?:[/?#].*)?$')
    re_image = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
    re_title = re.compile(r'data-title="(.*?)"')
    re_title_sanitize = re.compile(r'(?:[^ -~]|[/:])+')

    pool = Pool()
    kwds = {'verbose': verbose}

    for album in albums:
        try:
            directory = album_hash = re_album_hash.match(album).group(1)

            with urlopen('http://imgur.com/a/' + album_hash) as in_url:
                content = in_url.read().decode()
        except:
            print_error('could not read album: ' + album)
            continue

        if titles:
            title_raw = re_title.search(content).group(1)
            title_unescaped = html_parser.unescape(title_raw)
            title_sanitized = re_title_sanitize.sub(' ', title_unescaped)
            directory += '-[%s]' % title_sanitized

        if not os.path.exists(directory):
            if verbose:
                print('making directory: ' + directory)

            os.makedirs(directory)

        for number, pair in enumerate(re_image.finditer(content)):
            filename = pair.group(1) + pair.group(2)
            url = 'http://i.imgur.com/' + filename

            if numbers:
                path = '%s/%d-%s' % (directory, number, filename)
            else:
                path = '%s/%s' % (directory, filename)

            pool.apply_async(save_image, args=(url, path), kwds=kwds)

    pool.close()
    pool.join()


def main():
    parser = ArgumentParser(prog=PROGRAM, description='Download Imgur albums')

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
