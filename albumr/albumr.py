import argparse
import json
import logging
import multiprocessing
import os
import re

import argparse_extensions
import requests
import six

from . import __version__

_ALBUM_HASH_RE = re.compile(r'^(?:.*/)?([A-Za-z0-9]{5})(?:[/?#].*)?$')
_IMAGES_RE = re.compile(r'"images":(\[.*)')
_TITLE_RE = re.compile(r'"title":"(.*?)","title_clean":')
_TITLE_SANITIZE_RE = re.compile(r'(?:[^ -~]|[/:])+')


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
  except (Exception, KeyboardInterrupt):
    logging.exception('could not save file: %s', path)


def save_albums(albums, numbers=False, titles=False):
  raw_decode = json.JSONDecoder().raw_decode
  unescape = six.moves.html_parser.HTMLParser().unescape
  pool = multiprocessing.Pool()

  for album in albums:
    try:
      album_hash = _ALBUM_HASH_RE.search(album).group(1)
      response = requests.get('https://imgur.com/a/%s/all' % album_hash)
      response.raise_for_status()
      images, _ = raw_decode(_IMAGES_RE.search(response.text).group(1))
    except Exception:
      logging.exception('could not read album: %s', album)
      continue

    album_dir = album_hash
    if titles:
      title_match = _TITLE_RE.search(response.text)
      if title_match:
        title = _TITLE_SANITIZE_RE.sub(' ', unescape(title_match.group(1)))
        album_dir = '%s-[%s]' % (album_hash, title)
      else:
        logging.warning('failed to extract album title')

    if not os.path.exists(album_dir):
      logging.info('making directory: %s', album_dir)
      os.makedirs(album_dir)

    for i, image in enumerate(images, start=1):
      orig_name = '%s%s' % (image['hash'], image['ext'])
      url = 'https://i.imgur.com/%s' % orig_name
      filename = ('%d-%s' % (i, orig_name)) if numbers else orig_name
      path = '%s/%s' % (album_dir, filename)
      pool.apply_async(save_image, args=(url, path))

  pool.close()
  pool.join()


def main():
  parser = argparse.ArgumentParser(
      usage='%(prog)s [<options>] [--] <album>...',
      description='Imgur album downloader')

  parser.add_argument(
      'albums',
      nargs='+',
      type=str,
      help='an album hash or URL',
      metavar='<album>')

  parser.add_argument(
      '-n',
      '--numbers',
      action=argparse_extensions.NegatableStoreTrueAction,
      help='prepend numbers to filenames; default: %(default)s')
  parser.add_argument(
      '-t',
      '--titles',
      action=argparse_extensions.NegatableStoreTrueAction,
      help='append album titles to directory names; default: %(default)s')
  parser.add_argument(
      '-v',
      '--version',
      action='version',
      version='%(prog)s ' + __version__)

  args = parser.parse_args()

  logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
  logging.getLogger('requests').setLevel(logging.WARNING)

  save_albums(args.albums, numbers=args.numbers, titles=args.titles)


if __name__ == '__main__':
  main()
