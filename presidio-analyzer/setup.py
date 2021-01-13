import os.path
from os import path

import setuptools

__version__ = ""
parent_directory = os.path.abspath(
    os.path.join(path.abspath(path.dirname(__file__)), os.pardir)
)
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
        "spacy==2.3",
        "regex==2020.11.13",
        "tldextract==3.1.0",
    ],
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
