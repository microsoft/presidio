#!/usr/bin/env python
import os.path
from os import path

from setuptools import setup, find_packages

requirements = ["flask==1.1.2"]

test_requirements = ["pytest>=3", "flask==1.1.2"]

__version__ = ""
parent_directory = os.path.abspath(
    os.path.join(path.abspath(path.dirname(__file__)), os.pardir)
)
with open(os.path.join(parent_directory, "VERSION")) as version_file:
    __version__ = version_file.read().strip()

setup(
    python_requires=">=3.5",
    version=__version__,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
    ],
    description="Persidio Anonymizer package - replaces analyzed text with desired values.",
    install_requires=requirements,
    license="MIT license",
    include_package_data=True,
    keywords="presidio_anonymizer",
    name="presidio_anonymizer",
    packages=find_packages(include=["presidio_anonymizer", "presidio_anonymizer.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/microsoft/presidio",
    zip_safe=False,
    trusted_host=["pypi.org"],
)
