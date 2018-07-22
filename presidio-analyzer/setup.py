import setuptools
import os.path

with open(os.path.dirname(os.path.abspath(__file__)) + '/../README.MD', "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="presidio_analyzer",
    version="0.0.1",
    author="Tomer Rosenthal",
    author_email="olipoopo@gmail.com",
    description="Presidio analyzer package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/presid-io/presidio",
    packages=setuptools.find_packages(exclude=('tests')),
    install_requires=[
        'spacy==2.0.11',
        'grpcio>=1.13.0',
        'grpcio-tools>=1.13.0',
        'regex>=2018.07.11',
        'validators>=0.12.2'],
    # dependency_links=[SPACY_MODEL],
    include_package_data=True,
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
