#!/usr/bin/env python3

# Nikita Kouevda
# 2014/11/27

from argparse import ArgumentParser
from html.parser import HTMLParser
import multiprocessing
import os
import re
import sys
from urllib.request import urlopen


def print_error(message):
  print('{}: {}'.format(sys.argv[0], message), file=sys.stderr)


def save_image(url, path, verbose=False):
  if os.path.exists(path):
    print_error('file exists: {}'.format(path))
    return

  try:
    with urlopen(url) as in_file:
      content = in_file.read()
    if verbose:
      print('saving file: {}'.format(path))
    with open(path, 'wb') as out_file:
      out_file.write(content)
  except:
    print_error('could not save file: {}'.format(path))


def save_albums(albums, numbers=False, titles=False, verbose=False):
  html_parser = HTMLParser()

  re_album_hash = re.compile(r'^(?:.*/)?([A-Za-z0-9]{5})(?:[/?#].*)?$')
  re_image = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
  re_title = re.compile(r'data-title="(.*?)"')
  re_title_sanitize = re.compile(r'(?:[^ -~]|[/:])+')

  pool = multiprocessing.Pool()

  for album in albums:
    try:
      album_hash = re_album_hash.search(album).group(1)
      with urlopen('http://imgur.com/a/{}'.format(album_hash)) as in_file:
        content = in_file.read().decode()
    except:
      print_error('could not read album: {}'.format(album))
      continue

    if titles:
      title_raw = re_title.search(content).group(1)
      title_unescaped = html_parser.unescape(title_raw)
      title_sanitized = re_title_sanitize.sub(' ', title_unescaped)
      directory = '{}-[{}]'.format(album_hash, title_sanitized)
    else:
      directory = album_hash

    if not os.path.exists(directory):
      if verbose:
        print('making directory: {}'.format(directory))
      os.makedirs(directory)

    for i, image_match in enumerate(re_image.finditer(content)):
      filename = '{}{}'.format(image_match.group(1), image_match.group(2))
      url = 'http://i.imgur.com/{}'.format(filename)
      if numbers:
        path = '{}/{:d}-{}'.format(directory, i, filename)
      else:
        path = '{}/{}'.format(directory, filename)
      pool.apply_async(save_image, args=(url, path, verbose))

  pool.close()
  pool.join()


def main():
  parser = ArgumentParser(description='Command-line Imgur album downloader')
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
