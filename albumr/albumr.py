import argparse
import logging
import multiprocessing
import os
import re

import requests
from six.moves import html_parser

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
  album_hash_re = re.compile(r'^(?:.*/)?([A-Za-z0-9]{5})(?:[/?#].*)?$')
  image_re = re.compile(r'"hash":"([A-Za-z0-9]{5,7})".+?"ext":"(.+?)"')
  title_re = re.compile(r'"title":"(.*?)","title_clean":')
  title_sanitize_re = re.compile(r'(?:[^ -~]|[/:])+')
  unescape = html_parser.HTMLParser().unescape

  pool = multiprocessing.Pool()

  for album in albums:
    try:
      album_hash = album_hash_re.search(album).group(1)
      response = requests.get('https://imgur.com/a/%s' % album_hash)
      response.raise_for_status()
    except:
      logging.exception('could not read album: %s', album)
      continue

    if titles:
      title_raw = title_re.search(response.text).group(1)
      title_unescaped = unescape(title_raw)
      title_sanitized = title_sanitize_re.sub(' ', title_unescaped)
      album_dir = '%s-[%s]' % (album_hash, title_sanitized)
    else:
      album_dir = album_hash

    if not os.path.exists(album_dir):
      logging.info('making directory: %s', album_dir)
      os.makedirs(album_dir)

    for i, image_match in enumerate(image_re.finditer(response.text)):
      orig_name = '%s%s' % (image_match.group(1), image_match.group(2))
      url = 'https://i.imgur.com/%s' % orig_name
      filename = ('%d-%s' % (i, orig_name)) if numbers else orig_name
      path = '%s/%s' % (album_dir, filename)
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
