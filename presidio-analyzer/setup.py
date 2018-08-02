import setuptools
import os.path

with open(os.path.dirname(os.path.abspath(__file__)) + '/../README.MD', "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="presidio_analyzer",
    version="0.1.0",
    author="Presidio team",
    author_email="presidioteam@microsoft.com",
    description="Presidio analyzer package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Microsoft/presidio",
    packages=setuptools.find_packages(exclude=('tests')),
    install_requires=[
        'spacy==2.0.11',
        'grpcio>=1.13.0',
        'grpcio-tools>=1.13.0',
        'tldextract>=2.2.0'],
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
