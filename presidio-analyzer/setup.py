"""Setup.py for Presidio Analyzer."""
import os.path
from os import path

import setuptools

__version__ = ""
this_directory = path.abspath(path.dirname(__file__))
parent_directory = os.path.abspath(os.path.join(this_directory, os.pardir))

with open(path.join(this_directory, "README.MD"), encoding="utf-8") as f:
    long_description = f.read()

try:
    with open(os.path.join(parent_directory, "VERSION")) as version_file:
        __version__ = version_file.read().strip()
except Exception:
    __version__ = os.environ.get("PRESIDIO_VERSION", "0.0.1-alpha")

setuptools.setup(
    name="presidio_analyzer",
    version=__version__,
    description="Presidio analyzer package",
    url="https://github.com/Microsoft/presidio",
    packages=[
        "presidio_analyzer",
        "presidio_analyzer.predefined_recognizers",
        "presidio_analyzer.nlp_engine",
        "presidio_analyzer.context_aware_enhancers",
    ],
    package_data={
        "presidio_analyzer": ["py.typed", "conf/*"],
    },
    trusted_host=["pypi.org"],
    tests_require=["pytest", "flake8>=3.7.9"],
    install_requires=[
        "spacy>=3.4.4, <4.0.0",
        "regex",
        "tldextract",
        "pyyaml",
        "phonenumbers>=8.12,<9.0.0",
    ],
    extras_require={
        "transformers": ["spacy_huggingface_pipelines"],
        "stanza": ["stanza", "spacy_stanza"],
        "azure-ai-language": ["azure-ai-textanalytics", "azure-core"],
    },
    include_package_data=True,
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
)
