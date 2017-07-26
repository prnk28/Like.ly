import sys
from setuptools import setup, find_packages

requires = [
    'requests>=1.0.4',
    'tqdm>=3.8.0'
]

if sys.version_info < (3, 2):
    requires.append('futures==2.2')

setup(
    name='instagram-scraper',
    version='1.5.3',
    description=("instagram-scraper is a command-line application written in Python"
                 " that scrapes and downloads an instagram user\'s photos and videos. Use responsibly."),
    url='https://github.com/rarcega/instagram-scraper',
    download_url='https://github.com/rarcega/instagram-scraper/tarball/1.5.3',
    author='Richard Arcega',
    author_email='hello@richardarcega.com',
    license='Public domain',
    packages=find_packages(exclude=['tests']),
    install_requires=requires,
    entry_points={
        'console_scripts': ['instagram-scraper=instagram_scraper.app:main'],
    },
    test_suite='nose.collector',
    zip_safe=False,
    keywords=['instagram', 'scraper', 'download', 'media', 'photos', 'videos']
)
