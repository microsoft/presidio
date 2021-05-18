# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]
### Changed

### Removed

### Deprecated

## [2.2.1] - 10.05.2021
### Changed
* Create CODE_OF_CONDUCT
* ADF templates docs
* Fix spark sample to run presidio in broadcast
* Ad-hoc recognizers
* Text Analytics Integration Sample
* Documentation update and samples validation
* Adding tagger to the spaCy model pipeline
* Sample notebook for remote recognizer (using Text Analytics)
* Add matplotlib to image-redactor
* Added custom lambda anonymizer
* Added add pii_verify_engine to the image-redactor


[unreleased]: https://github.com/microsoft/presidio/compare/2.2.1...HEAD
[2.2.1]: https://github.com/microsoft/presidio/compare/2.2.0...2.2.1

## [2.2.0] - 12.04.2021
### Changed
#### Analyzer:
Upgrade Analyzer spacy version to 3.0.5

#### Anonymizer Engine:
1. Request entity AnonymizerConfig renamed OperatorConfig
    - In OperatorConfig: anonymizer_name -> operator_name
2. Response entity AnonymizerResult renamed to EngineResult
    - In EngineResult: List[AnonymizedEntity] -> List[OperatorResult]
    - In OperatorResult: 
        - anonymizer -> operator
        - anonymized_text -> text

#### Anonymize API:
1. Response entity anonymizer renamed to operator.
2. Response entity anonymizer_text renamed to text.

#### Deanonymize:
New endpoint for deanonymizing encrypted entities by the anonymizer.

[unreleased]: https://github.com/microsoft/presidio/compare/2.2.0...HEAD
[2.2.0]: https://github.com/microsoft/presidio/compare/2.1.0...2.2.0
