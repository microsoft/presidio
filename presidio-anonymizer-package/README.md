# PII-Obfuscation Command Line Tool

## Build source discribution
First please install the presidio-analyzer package by following the instructions [here](https://github.com/microsoft/presidio/blob/master/docs/deploy.md#install-presidio-analyzer-as-a-python-package).
Then by running `python setup.py sdist`, an `pii-obfuscation-0.1.0.tar.gz` file will be genernated in `dist` folder. 

## Installation 
Install by using the source distribution with pip
`pip install dist/pii-obfuscation-0.1.0.tar.gz`

## Usage
After the installation, the command line tool can be run by `pii-obfuscation` on terminal.
To varify installation or check how to use, do `pii-obfuscation --help` and will get following output.

```
Group
    pii-obfuscation

Commands:
    directory : Obfuscator text files under input directory and store to output directory
                pii-obfuscation directory --input-path <raw files folder> --output-path <obfuscated files folder>.
    text      : Obfuscate a single piece of text 
                pii-obfuscation text --text "John Smith drivers license is AC432223".

```
### Alias Description
For an example alias `DEFAULT_DOMAIN_<PERSON_1>`, `DEFAULT_DOMAIN` is a prefix to distinguish different domains which could be defined by user.
`PERSON` is the named entity type to which the noun phrase corresponding to this alias belongs. `1` is an id for this alias to avoid repeated aliases, so
 the aliases in the same domain should have different ids.


### Obfuscate a piece of text
To do obfuscation on a piece of text or to simply verify if the obfuscation process works. Do `pii-obfuscation text --text "John Smith drivers license is AC432223"` 

The success out put going to be:

```
DEFAULT_DOMAIN_<PERSON_1> drivers license is DEFAULT_DOMAIN_<US_DRIVER_LICENSE_2>

```

### Obfuscate a group of documents

The main functionality is obfuscate a group of documents, given an `input-path` the `pii-obfuscation` tool will scan the files under the input folder and store the anonymized files to an output folder. E.g. By executing the following command 

```pii-obfuscation directory --input-path=data/input --output-path=data/output``` 

in an directory with following structure 

```
- data
    - input
        - data1.txt
        - data2.txt
        - data3.txt

    - output
```
the output in stdout will be the PII lookup table and anonymized `data1.txt`, `data2.txt`, `data3.txt` will be stored in output directory.

### Parameters

*   `--fields` states a list of PII types for obfuscation
*   `--domain-name` states a user defined domain name as a prefix to the alias. So by setting different domain names, same noun phrases could be masked by different alias





