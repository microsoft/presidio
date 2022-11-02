# -*- coding: utf-8 -*-

from setuptools import setup
import os.path
from presidio_cli import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
)

readme = ""
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "rb") as stream:
        readme = stream.read().decode("utf8")

setup(
    name=APP_NAME,
    version=APP_VERSION,
    url="https://github.com/microsoft/presidio/presidio-cli",
    description=APP_DESCRIPTION.split("\n")[0],
    long_description=readme,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=["presidio-analyzer>=2.2", "pyyaml", "pathspec"],
    trusted_host=["pypi.org"],
    tests_require=["pytest", "flake8>=3.7.9"],
)
