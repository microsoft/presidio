import setuptools
import os.path
from os import path

__version__ = ""
this_directory = path.abspath(path.dirname(__file__))
with open(os.path.join(this_directory, 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

setuptools.setup(
    name="presidio_analyzer",
    version=__version__,
    description="Presidio analyzer package",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/Microsoft/presidio",
    packages=[
        'analyzer', 'analyzer.predefined_recognizers', 'analyzer.nlp_engine',
        'analyzer.recognizer_registry'
    ],
    trusted_host=['pypi.org'],
    tests_require=['pytest', 'flake8', 'pylint==2.3.1'],
    install_requires=[
        'cython==0.29.10',
        'spacy==2.1.4',
        'regex==2019.6.8',
        'grpcio==1.21.1',
        'protobuf==3.8.0',
        'tldextract==2.2.1',
        'knack==0.6.2'],
    include_package_data=True,
    license='MIT',
    scripts=[
        'analyzer/presidio-analyzer',
        'analyzer/presidio-analyzer.bat',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
