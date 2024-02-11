#!/usr/bin/env python
# noqa: D100
import os.path
from os import path

from setuptools import setup, find_packages

test_requirements = ["pytest>=3", "flake8==3.7.9"]

__version__ = ""
this_directory = path.abspath(path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(this_directory, os.pardir))

with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

try:
    with open(
        os.path.join(parent_directory, "PRESIDIO-STRUCTURED-VERSION")
    ) as version_file:
        __version__ = version_file.read().strip()
except Exception:
    __version__ = os.environ.get("PRESIDIO_STRUCTURED_VERSION", "0.0.1-alpha")

setup(
    name="presidio_structured",
    python_requires=">=3.5",
    version=__version__,
    packages=find_packages(include=["presidio_structured", "presidio_structured.*"]),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    description="Presidio structured package - analyzes and anonymizes \
          structured and semi-structured data.",
    license="MIT license",
    include_package_data=True,
    keywords="presidio_structured",
    install_requires=["presidio-analyzer>=2.2", "presidio-anonymizer>=2.2"],
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/microsoft/presidio",
    zip_safe=False,
    trusted_host=["pypi.org"],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
