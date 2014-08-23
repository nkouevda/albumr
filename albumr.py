#!/usr/bin/env python3

# Nikita Kouevda
# 2014/08/22

from argparse import ArgumentParser
from html.parser import HTMLParser
from multiprocessing import Pool
import os
import re
import sys
from urllib.request import urlopen


PROGRAM = os.path.basename(__file__)


def print_error(message):
  print('%s: %s' % (PROGRAM, message), file=sys.stderr)


def save_image(url, path, verbose=False):
  if os.path.exists(path):
    print_error('file exists: %s' % path)
    return

  try:
    with urlopen(url) as in_file:
      content = in_file.read()

    if verbose:
      print('saving file: %s' % path)

    with open(path, 'wb') as out_file:
      out_file.write(content)
  except:
    print_error('could not save file: %s' % path)


def save_albums(albums, numbers=False, titles=False, verbose=False):
  html_parser = HTMLParser()

  re_album_hash = re.compile(r'^(?:.*/)?([A-Za-z0-9]{5})(?:[/?#].*)?$')
  re_image = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
  re_title = re.compile(r'data-title="(.*?)"')
  re_title_sanitize = re.compile(r'(?:[^ -~]|[/:])+')

  pool = Pool()
  kwargs = {'verbose': verbose}

  for album in albums:
    try:
      album_hash = re_album_hash.search(album).group(1)

      with urlopen('http://imgur.com/a/%s' % album_hash) as in_file:
        content = in_file.read().decode()
    except:
      print_error('could not read album: %s' % album)
      continue

    if titles:
      title_raw = re_title.search(content).group(1)
      title_unescaped = html_parser.unescape(title_raw)
      title_sanitized = re_title_sanitize.sub(' ', title_unescaped)
      directory = '%s-[%s]' % (album_hash, title_sanitized)
    else:
      directory = album_hash

    if not os.path.exists(directory):
      if verbose:
        print('making directory: %s' % directory)

      os.makedirs(directory)

    for i, image_match in enumerate(re_image.finditer(content)):
      filename = '%s%s' % (image_match.group(1), image_match.group(2))
      url = 'http://i.imgur.com/%s' % filename

      if numbers:
        path = '%s/%d-%s' % (directory, i, filename)
      else:
        path = '%s/%s' % (directory, filename)

      pool.apply_async(save_image, args=(url, path), kwds=kwargs)

  pool.close()
  pool.join()


def main():
  parser = ArgumentParser(prog=PROGRAM,
                          description='Command-line Imgur album downloader')

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
