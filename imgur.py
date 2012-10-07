#!/usr/bin/env python3

# Nikita Kouevda
# 2012/10/07

import argparse, json, os, re, sys
from urllib.request import urlopen

def extract_images(album):
    """Given a standard alphanumeric album name of the form ABCDE, return a
    list of the images contained in the album, each of the form FGHIJ.XYZ."""

    try:
        # Read and decode the page
        page = urlopen("http://imgur.com/a/" + album).read().decode()

        # Extract the list of images and eval it to a Python list
        images = json.loads(re.search(r'(?<="items":)\[\{.+\}\](?=\})',
                page).group())

        # Generate a list of images in the album
        return [image["hash"] + image["ext"] for image in images]
    except:
        print("error: could not read album: " + album)
        return []

def save_images(album, images, verbose=False):
    """Given a list of images, each of the form FGHIJ.XYZ, save each image under
    a local directory of the same name as the album."""

    # Create the directory if it does not exist
    if not os.path.exists(album):
        if verbose:
            print("making directory: " + album)

        os.makedirs(album)

    # Count number of saved images for later verification
    saved_count = 0

    # Save each image
    for image in images:
        path, url = album + "/" + image, "http://i.imgur.com/" + image

        if os.path.exists(path):
            print("error: file exists: " + path)
        else:
            if verbose:
                print("downloading: " + url)

            try:
                # Read but do not decode image data
                image_data = urlopen(url).read()
            except:
                print("error: could not download file: " + url)
                continue

            if verbose:
                print("saving: " + path + " (" + str(saved_count + 1) + " of " +
                        str(len(images)) + ")")

            try:
                # Write image data in binary
                with open(path, "wb") as out_file:
                    out_file.write(image_data)

                saved_count += 1
            except:
                print("error: could not save file: " + path)

    # Print final statistics
    print("saved " + str(saved_count) + " of " + str(len(images)) + \
        " images from " + album)

def main():
    # Create an argument parser
    parser = argparse.ArgumentParser(description="Download Imgur albums")

    # The album name(s), with at least one required
    parser.add_argument("albums", nargs='+', type=str, help="The album hash, \
consisting of 5 alphanumeric characters.", metavar="album")

    # Verbose output
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose \
output.")

    # Parse command-line arguments
    args = parser.parse_args()

    # Process each album separately
    for album in args.albums:
        # Extract image urls
        image_urls = extract_images(album)

        # Save the images, if any, using the album name as the subdirectory
        if len(image_urls) > 0:
            save_images(album, image_urls, verbose=args.verbose)

if __name__ == '__main__':
    main()
