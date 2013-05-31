#!/usr/bin/env python3

# Nikita Kouevda
# 2013/05/31

import argparse
import multiprocessing
import os
import re
from urllib.request import urlopen


def save_image(image_tuple):
    # Unpack the album, number, and image
    album, number, image = image_tuple

    # Save each file 'http://i.imgur.com/[image]' to '[album]/[number]-[image]'
    url = 'http://i.imgur.com/' + image
    local_path = '{0}/{1}-{2}'.format(album, number, image)

    if os.path.exists(local_path):
        print('error: file exists: ' + local_path)
    else:
        try:
            # Read and write the binary image data
            with urlopen(url) as in_url:
                with open(local_path, 'wb') as out_file:
                    print('saving file: ' + local_path)
                    out_file.write(in_url.read())
        except:
            print('error: could not save file: ' + local_path)


def main():
    parser = argparse.ArgumentParser(description="Download Imgur albums")

    # Require at least one album name
    parser.add_argument(
        'albums', nargs='+', type=str, help='an album hash or URL',
        metavar='album')

    # Parse the given command-line arguments
    args = parser.parse_args()

    images = set()

    for album in args.albums:
        try:
            # Extract the album hash
            album = re.match(
                r'(?:.*/)?([A-Za-z0-9]{5}?)(?:#.*)?$', album).group(1)

            # Read and decode the content
            with urlopen('http://imgur.com/a/' + album) as in_url:
                content = in_url.read().decode()
        except:
            print('error: could not read album: ' + album)
            continue

        # Find all pairs of image hashes and extensions in the content
        pairs = re.finditer(
            r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"', content)

        # Create the directory for this album if it does not exist
        if not os.path.exists(album):
            print('making directory: ' + album)
            os.makedirs(album)

        # Add each image to the set, along with its album and number
        for number, pair in enumerate(pairs):
            images.add((album, number + 1, pair.group(1) + pair.group(2)))

    # Use a process pool to simultaneously save images
    pool = multiprocessing.Pool()
    pool.imap_unordered(save_image, images)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
