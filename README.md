# albumr

Imgur album downloader.

## Installation

    pip install albumr

## Usage

    usage: albumr [-h] [-n] [-t] album [album ...]

    Imgur album downloader

    positional arguments:
      album          an album hash or URL

    optional arguments:
      -h, --help     show this help message and exit
      -n, --numbers  prepend numbers to filenames
      -t, --titles   append album titles to directory names

## Examples

From album URL:

    albumr http://imgur.com/a/adkET

From album hash, with numbers in filenames and album title in directory name:

    albumr -nt adkET

## License

Licensed under the [MIT License](http://www.opensource.org/licenses/MIT).
