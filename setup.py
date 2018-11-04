#!/usr/bin/env python

from pathlib import Path
from configparser import ConfigParser

from setuptools import setup, find_packages


def packages_from_pipfile(section):
    pipfile_path = str((Path(__file__).parent / 'Pipfile').absolute())
    parser = ConfigParser()
    parser.read(pipfile_path)
    return [f'{k}=={v}' for k, v in parser[section].items()]


setup(
    name='tipy',
    version='0.0.1',
    description='Python libray for displaying images on terminal',
    author='Masahiro Wada',
    author_email='argon.argon.argon@gmail.com',
    url='https://github.com/ar90n/tipy',
    install_requires=packages_from_pipfile('packages'),
    extras_require={
        "develop": packages_from_pipfile('dev-packages'),
    },
    packages=find_packages('src'),
    package_dir={'':'src'}
)
