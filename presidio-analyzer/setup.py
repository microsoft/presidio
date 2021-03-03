"""Setup.py for Presidio Analyzer."""
import os.path
from os import path

import setuptools

__version__ = ""
this_directory = path.abspath(path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(this_directory, os.pardir))

with open(path.join(this_directory, 'README.MD'), encoding='utf-8') as f:
    long_description = f.read()

with open(os.path.join(parent_directory, "VERSION")) as version_file:
    __version__ = version_file.read().strip()

setuptools.setup(
    name="presidio_analyzer",
    version=__version__,
    description="Presidio analyzer package",
    url="https://github.com/Microsoft/presidio",
    packages=[
        "presidio_analyzer",
        "presidio_analyzer.predefined_recognizers",
        "presidio_analyzer.nlp_engine",
        "presidio_analyzer.recognizer_registry",
    ],
    trusted_host=["pypi.org"],
    tests_require=["pytest", "flake8==3.7.9"],
    install_requires=[
        "spacy==3.0.3",
        "regex==2020.11.13",
        "tldextract==3.1.0",
        "pyyaml==5.4.1",
    ],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)
