<!-- Nikita Kouevda -->
<!-- 2014/12/14 -->

# albumr

Command-line Imgur album downloader.

## Usage

    usage: albumr.py [-h] [-n] [-t] [-v] album [album ...]

    Command-line Imgur album downloader

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
