import setuptools

setuptools.setup(
    name="pii-obfuscation",
    version="0.1.0",
    # author="TR",
    # author_email="TR",
    description="pii obfuscation anonymizer package",
    packages=[
        'anonymizer',
        'anonymizer.db'
    ],
    install_requires=[
        'cython>=0.28.5',
        'tldextract>=2.2.0', 'knack>=0.4.2', 'spacy>=2.1.3',
        'en_core_web_lg @ https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-2.1.0/en_core_web_lg-2.1.0.tar.gz'
    ],
    include_package_data=True,
    license='MIT',
    scripts=[
        'anonymizer/pii-obfuscation',
        'anonymizer/pii-obfuscation.bat',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
