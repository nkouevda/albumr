<!-- Nikita Kouevda -->
<!-- 2015/05/23 -->

# albumr

Imgur album downloader.

## Setup

    pip install -r requirements.txt

## Usage

    usage: albumr.py [-h] [-n] [-t] [-v] album [album ...]

    Imgur album downloader

    positional arguments:
    album          an album hash or URL

    optional arguments:
    -h, --help     show this help message and exit
    -n, --numbers  prepend numbers to filenames
    -t, --titles   append album titles to directory names
    -v, --verbose  verbose output

## Examples

From album URL:

    ./albumr.py http://imgur.com/a/adkET

From album hash, with numbers in filenames, album title in directory name, and
verbose output:

    ./albumr.py -ntv adkET

## License

Licensed under the [MIT License](http://www.opensource.org/licenses/MIT).
