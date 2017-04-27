from setuptools import setup

with open('README.md', 'r') as f:
  readme = f.read()

setup(
    name='albumr',
    version='1.0.4',
    description='Imgur album downloader',
    long_description=readme,
    url='https://github.com/nkouevda/albumr',
    author='Nikita Kouevda',
    author_email='nkouevda@gmail.com',
    license='MIT',
    packages=['albumr'],
    install_requires=[
        'requests',
        'six',
    ],
    entry_points={
        'console_scripts': [
            'albumr=albumr.albumr:main',
        ],
    },
)
