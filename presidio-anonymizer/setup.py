#!/usr/bin/env python
# noqa: D100
import os.path
from os import path

from setuptools import setup, find_packages

test_requirements = ["pytest>=3", "flake8==3.7.9", "flask==1.1.2"]

__version__ = ""
this_directory = path.abspath(path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(this_directory, os.pardir))

with open(path.join(this_directory, 'README.MD'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(parent_directory, "VERSION")) as version_file:
    __version__ = version_file.read().strip()

setup(
    name="presidio_anonymizer",
    python_requires=">=3.5",
    version=__version__,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    description="Persidio Anonymizer package - replaces analyzed text with desired "
                "values.",
    license="MIT license",
    include_package_data=True,
    keywords="presidio_anonymizer",
    packages=find_packages(include=["presidio_anonymizer", "presidio_anonymizer.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/microsoft/presidio",
    zip_safe=False,
    trusted_host=["pypi.org"],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
