"""Setup.py for Presidio Image Redactor."""
import os.path
from os import path

from setuptools import setup, find_packages

requirements = [
    "pillow>=9.0",
    "pytesseract>=0.3.7,<0.4",
    "presidio-analyzer>=1.9.0",
    "matplotlib>=3.6",
    "pydicom>=2.3.0",
    "pypng>=0.20220715.0",
]

test_requirements = ["pytest>=3", "pytest-mock>=3.10.0", "flake8>=3.7.9"]

__version__ = ""
this_directory = path.abspath(path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(this_directory, os.pardir))

with open(path.join(this_directory, "README.MD"), encoding="utf-8") as f:
    long_description = f.read()

with open(os.path.join(parent_directory, "VERSION-IMAGE-REDACTOR")) as version_file:
    __version__ = version_file.read().strip()

setup(
    name="presidio-image-redactor",
    python_requires=">=3.5",
    version=__version__,
    description="Presidio image redactor package",
    url="https://github.com/Microsoft/presidio",
    packages=find_packages(exclude=["tests"]),
    test_suite="tests",
    trusted_host=["pypi.org"],
    tests_require=test_requirements,
    install_requires=requirements,
    include_package_data=True,
    license="MIT",
    keywords="presidio_image_redactor",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
