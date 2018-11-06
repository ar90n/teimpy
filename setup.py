#!/usr/bin/env python

from pathlib import Path
from configparser import ConfigParser

from setuptools import setup, find_packages


def get_path(file):
    return Path(__file__).parent / file


def packages_from_pipfile(section):
    pipfile_path = str(get_path('Pipfile'))
    parser = ConfigParser()
    parser.read(pipfile_path)

    result = []
    for k, v in parser[section].items():
        pkg = k if v == '"*"' else '{}=={}'.format(k, v)
        result.append(pkg)
    return result


with get_path('README.md').open() as f:
    readme = f.read()

setup(
    name='teimpy',
    version='0.0.1',
    license='MIT',
    description='Python libray for displaying images on terminal',
    long_description=readme,

    author='Masahiro Wada',
    author_email='argon.argon.argon@gmail.com',
    url='https://github.com/ar90n/teimpy',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    install_requires=packages_from_pipfile('packages'),
    extras_require={
        'develop': packages_from_pipfile('dev-packages'),
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
