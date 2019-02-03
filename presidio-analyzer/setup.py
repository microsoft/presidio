import setuptools

# with open(os.path.dirname(os.path.abspath(__file__)) + '/../README.MD', "r") as fh:
#     long_description = fh.read()

setuptools.setup(
  name="presidio_analyzer",
  version="0.1.0",
  author="Presidio team",
  author_email="torosent@microsoft.com",
  description="Presidio analyzer package",
  # long_description=long_description,
  # long_description_content_type="text/markdown",
  url="https://github.com/Microsoft/presidio",
  packages=[
    'analyzer', 'analyzer.field_types', 'analyzer.field_types.us',
    'analyzer.field_types.globally'
  ],
  install_requires=[
    'grpcio>=1.13.0', 'cython>=0.28.5', 'protobuf>=3.6.0',
    'tldextract>=2.2.0', 'knack>=0.4.2', 'spacy>=2.0.18'
  ],
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
