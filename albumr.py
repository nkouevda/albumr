#!/usr/bin/env python3

# Nikita Kouevda
# 2015/05/23

import argparse
import html
import logging
import multiprocessing
import os
import re

import requests


def save_image(url, path):
  if os.path.exists(path):
    logging.error('file exists: %s', path)
    return

  try:
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as out_file:
      out_file.write(response.content)
    logging.info('saved file: %s', path)
  except:
    logging.exception('could not save file: %s', path)


def save_albums(albums, numbers=False, titles=False):
  re_album_hash = re.compile(r'^(?:.*/)?([A-Za-z0-9]{5})(?:[/?#].*)?$')
  re_image = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
  re_title = re.compile(r'data-title="(.*?)"')
  re_title_sanitize = re.compile(r'(?:[^ -~]|[/:])+')

  pool = multiprocessing.Pool()

  for album in albums:
    try:
      album_hash = re_album_hash.search(album).group(1)
      response = requests.get('http://imgur.com/a/{}'.format(album_hash))
      response.raise_for_status()
    except:
      logging.exception('could not read album: %s', album)
      continue

    if titles:
      title_raw = re_title.search(response.text).group(1)
      title_unescaped = html.unescape(title_raw)
      title_sanitized = re_title_sanitize.sub(' ', title_unescaped)
      album_dir = '{}-[{}]'.format(album_hash, title_sanitized)
    else:
      album_dir = album_hash

    if not os.path.exists(album_dir):
      logging.info('making directory: %s', album_dir)
      os.makedirs(album_dir)

    for i, image_match in enumerate(re_image.finditer(response.text)):
      orig_name = '{}{}'.format(image_match.group(1), image_match.group(2))
      url = 'http://i.imgur.com/{}'.format(orig_name)
      filename = '{:d}-{}'.format(i, orig_name) if numbers else orig_name
      path = '{}/{}'.format(album_dir, filename)
      pool.apply_async(save_image, args=(url, path))

  pool.close()
  pool.join()


def main():
  parser = argparse.ArgumentParser(description='Imgur album downloader')
  parser.add_argument('albums', nargs='+', type=str, metavar='album',
                      help='an album hash or URL')
  parser.add_argument('-n', '--numbers', action='store_true',
                      help='prepend numbers to filenames')
  parser.add_argument('-t', '--titles', action='store_true',
                      help='append album titles to directory names')
  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
  logging.getLogger('requests').setLevel(logging.WARNING)

  save_albums(args.albums, numbers=args.numbers, titles=args.titles)


if __name__ == '__main__':
  main()
