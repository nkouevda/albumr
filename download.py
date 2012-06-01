#!/usr/bin/env python3

# Nikita Kouevda
# 2012/06/01

import os, sys
from urllib.request import urlopen

def extract_images(album):
    """Given a standard alphanumeric album name (of the form ABCDE), returns a
    list of the images contained in the album (each of the form FGHIJ.xyz)."""

    try:
        # Read and decode the page
        page = urlopen("http://imgur.com/a/" + album).read().decode()

        # Define null to avoid parse error
        null = None

        # Extract the list of images and eval it to a Python list
        image_list = eval(page[page.find('"items":') + 8:page.find("}]}") + 2])

        # Generate a list of images in the album
        return [image["hash"] + image["ext"] for image in image_list]
    except:
        print("error: could not read album: " + album)
        return []

def save_images(directory, images):
    """Given a list of images (each of the form FGHIJ.xyz), saves each image
    under the specified directory."""

    # Create the directory if it does not exist
    if (not os.path.exists(directory)):
        os.makedirs(directory)

    # Count number of saved images to verify later
    saved = 0

    # Save each image
    for image in images:
        path = directory + "/" + image

        if (os.path.exists(path)):
            print("file exists: " + path)
        else:
            print("downloading: " + path)

            try:
                image_data = urlopen("http://i.imgur.com/" + image).read()
            except:
                print("error: could not download file")
                continue

            try:
                with open(path, "wb") as out_file:
                    out_file.write(image_data)

                saved += 1
            except:
                print("error: could not save file")

    # Print final output statistics
    print("saved " + str(saved) + " of " + str(len(images)) + " images")

def main():
    """Takes one command-line argument, the album name, and saves all images
    contained in that album to a local directory."""

    # Use the first argument as the album name
    if (len(sys.argv) < 2):
        print("error: please pass an album name")
    else:
        album = sys.argv[1]

        # Extract image urls
        image_urls = extract_images(album)

        # Save the images
        if (len(image_urls) > 0):
            save_images(album, image_urls)

if (__name__ == '__main__'):
    main()
