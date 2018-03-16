from setuptools import setup

version = {}

with open('albumr/__version__.py', 'r') as f:
  exec(f.read(), version)

with open('README.md', 'r') as f:
  readme = f.read()

setup(
    name='albumr',
    version=version['__version__'],
    description='Imgur album downloader',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/nkouevda/albumr',
    author='Nikita Kouevda',
    author_email='nkouevda@gmail.com',
    license='MIT',
    packages=['albumr'],
    install_requires=[
        'argparse-extensions',
        'requests',
        'six',
    ],
    entry_points={
        'console_scripts': [
            'albumr=albumr.albumr:main',
        ],
    },
)
