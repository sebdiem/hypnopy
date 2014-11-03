# -*- coding: utf8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

    config = {
    'description': 'A new project',
    'author': 'Sébastien Diemer',
    'url': 'https://github.com/sebdiem/hypnopy',
    'download_url': 'https://github.com/sebdiem/hypnopy',
    'author_email': 'diemersebastien@yahoo.fr',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['hypnopy'],
    'scripts': [],
    'name': 'hypnopy'
}

setup(**config)
