#!/usr/bin/env python3

# Nikita Kouevda
# 2013/08/03

import argparse
import html.parser
import multiprocessing
import os
import re
from urllib.request import urlopen


def save_image(directory_number_image_verbose):
    directory, number, image, verbose = directory_number_image_verbose

    # Save 'http://i.imgur.com/`image`' to '`directory`/`number`-`image`'
    url = 'http://i.imgur.com/' + image
    path = '{0}/{1}-{2}'.format(directory, number, image)

    if os.path.exists(path):
        print('error: file exists: ' + path)
    else:
        try:
            with urlopen(url) as in_url:
                with open(path, 'wb') as out_file:
                    if verbose:
                        print('saving file: ' + path)

                    out_file.write(in_url.read())
        except:
            print('error: could not save file: ' + path)


def save_albums(albums, include_title=False, verbose=False):
    html_parser = html.parser.HTMLParser()
    re_album_hash = re.compile(r'(?:.*/)?([A-Za-z0-9]{5})(?:[/#].*)?$')
    re_image = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
    re_title = re.compile(r'data-title="(.*?)"')
    re_title_sanitize = re.compile(r'(?:[^ -~]|[/:])+')

    images = set()

    for album in albums:
        try:
            directory = album_hash = re_album_hash.match(album).group(1)

            with urlopen('http://imgur.com/a/' + album_hash) as in_url:
                content = in_url.read().decode()
        except:
            print('error: could not read album: ' + album)
            continue

        if include_title:
            # Extract the title, sanitize it, and include it in the directory
            title_raw = re_title.search(content).group(1)
            title_parsed = html_parser.unescape(title_raw)
            title_sanitized = re_title_sanitize.sub(' ', title_parsed)
            directory += '-[' + title_sanitized + ']'

        if not os.path.exists(directory):
            if verbose:
                print('making directory: ' + directory)

            os.makedirs(directory)

        # Add each image and its relevant information to the set
        for number, pair in enumerate(re_image.finditer(content)):
            image = pair.group(1) + pair.group(2)
            images.add((directory, number + 1, image, verbose))

    # Use a process pool to simultaneously save images
    pool = multiprocessing.Pool()
    pool.imap_unordered(save_image, images)
    pool.close()
    pool.join()


def main():
    parser = argparse.ArgumentParser(description='Download Imgur albums')

    # Require at least one album
    parser.add_argument('albums', nargs='+', type=str, metavar='album',
                        help='an album hash or URL')

    parser.add_argument('-t', '--title', action='store_true',
                        help='append album title to directory name')

    parser.add_argument('-v', '--verbose', action='store_true',
                        help='verbose output')

    args = parser.parse_args()

    save_albums(args.albums, include_title=args.title, verbose=args.verbose)


if __name__ == '__main__':
    main()
