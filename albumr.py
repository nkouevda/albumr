#!/usr/bin/env python3

# Nikita Kouevda
# 2013/06/06

import argparse
import html.parser
import multiprocessing
import os
import re
from urllib.request import urlopen


def save_image(directory_number_image_verbose):
    directory, number, image, verbose = directory_number_image_verbose

    # Save 'http://i.imgur.com/$image' to '$directory/$number-$image'
    url = 'http://i.imgur.com/' + image
    path = '{0}/{1}-{2}'.format(directory, number, image)

    if os.path.exists(path):
        print('error: file exists: ' + path)
    else:
        try:
            # Read and write the binary image data
            with urlopen(url) as in_url:
                with open(path, 'wb') as out_file:
                    if verbose:
                        print('saving file: ' + path)

                    out_file.write(in_url.read())
        except:
            print('error: could not save file: ' + path)


def main():
    parser = argparse.ArgumentParser(description="Download Imgur albums")

    # Require at least one album name
    parser.add_argument(
        'albums', nargs='+', type=str, metavar='album',
        help='an album hash or URL')

    parser.add_argument(
        '-t', '--title', action='store_true',
        help='append album title to directory name')

    parser.add_argument(
        '-v', '--verbose', action='store_true', help='verbose output')

    # Parse the given command-line arguments
    args = parser.parse_args()

    images = set()

    for album in args.albums:
        try:
            # Determine the album hash
            directory = album = re.match(
                r'(?:.*/)?([A-Za-z0-9]{5}?)(?:#.*)?$', album).group(1)

            # Read and decode the album page's content
            with urlopen('http://imgur.com/a/' + album) as in_url:
                content = in_url.read().decode()
        except:
            print('error: could not read album: ' + album)
            continue

        if args.title:
            # Extract the title, sanitize it, and append it to the directory
            title = re.search(r'data-title="(.*?)"', content).group(1)
            title = html.parser.HTMLParser().unescape(title)
            title = re.sub(r'(?:[^ -~]|[/:])+', ' ', title)
            directory += '-[' + title + ']'

        # Find all pairs of image hashes and extensions in the content
        pairs = re.finditer(
            r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"', content)

        if not os.path.exists(directory):
            if args.verbose:
                print('making directory: ' + directory)

            os.makedirs(directory)

        # Add each image and its relevant information to the set
        for number, pair in enumerate(pairs):
            image = pair.group(1) + pair.group(2)
            images.add((directory, number + 1, image, args.verbose))

    # Use a process pool to simultaneously save images
    pool = multiprocessing.Pool()
    pool.imap_unordered(save_image, images)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
