# albumr

Imgur album downloader.

## Installation

    pip install albumr

## Usage

```
usage: albumr [<options>] [--] <album>...

Imgur album downloader

positional arguments:
  album                 an album hash or URL

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -n, --numbers, --no-numbers
                        prepend numbers to filenames; default: False
  -t, --titles, --no-titles
                        append album titles to directory names; default: False
```

## Examples

From album URL:

    albumr http://imgur.com/a/adkET

From album hash, with numbers in filenames and album title in directory name:

    albumr -nt adkET

## License

Licensed under the [MIT License](http://www.opensource.org/licenses/MIT).
