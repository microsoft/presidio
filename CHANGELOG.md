# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
#### Analyzer
#### Anonymizer
#### Image redactor
#### Structured


### Changed

### Removed


## [2.2.353] - Feb 12th 2024

### Added
#### Analyzer
* Add predefined_recognizer: IN_AADHAAR (#1256)

#### Anonymizer
* Added the option to add custom operators + pseudonymization sample (#1284)

### Changed

#### Analyzer
* Fix failing test due to optional package (#1258)
* Update publish-to-pypi.yml (#1259)
* Allow local Spacy Models to be loaded in NLP Engine (#1269)
* Upgrade pip in windows containers (#1272)

#### Image Redactor
* Bugfix in ImageAnalyzerEngine  #1274


## [2.2.352] - Jan 22nd 2024
### Added
#### Structured
* Added alpha of presidio-structured, a library (presidio-structured) which re-uses existing logic from existing presidio components to allow anonymization of (semi-)structured data. (#1192)

#### Analyzer
* Add PL PESEL recognizer (#1209)
* Azure AI language recognizer (#1228)
* Add_conf_to_package_data (#1243)

#### Anonymizer
* Add keep operator as deanonymizer (#1255)
* Update anonymize_list type hints and document that sometimes items will be ignored. (#1252)


#### General
* Add Dockerfile for Windows containers (#1194)

### Changed
#### Analyzer
* Drop WA driver license number (#1214)
* Change ner_model_configuration from list to map (#1222)
* Bugfix in SpacyRecognizer (#1221)
* Bugfix in NerModelConfiguration (#1230)
* Add_conf_to_package_data (#1243)

#### Anonymizer
* Improved the logic of conflict handling in AnonymizerEngine (#1196)

#### Image Redactor
* Change default score threshold in image redactor (#1210)
* fixes bug #1227 (#1231)
* Added missing dependencies for opencv-python and azure forms recognizer (#1257)

#### General
* Remove inclusive-lint step (#1207)
* Updates to demo website with new NLP Engine (#1181)


## [2.2.351] - Nov. 6th 2024
### Changed
#### Analyzer
* Hotfix for NerModelConfiguration not created correctly (#1208)

## [2.2.350] - Nov. 2nd 2024
### Changed
#### Analyzer
* Hotfix: default.yaml is not parsed correctly (#1202)

## [2.2.35] - Nov. 2nd 2024
### Changed
#### Analyzer
* Put org in ignore as it has many FPs (#1200)


## [2.2.34] - Oct. 30th 2024

### Added
#### Analyzer
* New Predefined Recognizer: IN_PAN (#1100)
  
#### Anonymizer
* Anonymizer - Pass bytes key to Encrypt / Decrypt (#1147)
  
#### Image redactor
* DICOM redactor improvement: Enabling more photometric interpretations (#1103)
* DICOM redactor improvement: Adding exceptions for when DICOM file does not have pixel data (#1104)
* Small reordering of kwargs as prereq for allow list functionality (#1110)
* DICOM redactor improvement: Preventing distortion when multiple sets of pixels are in one instance (#1109)
* DICOM redactor improvement: Enabling compatibility with compressed images (#1105)
* DICOM redactor improvement: Enable return of redacted bboxes (#1111)
* DICOM redactor improvement: Enable selection of redact approach (#1113)
* Enable toggle of printing output location after redacting from file (#1144)
* Changing test exception type check (#1148)
* Enabling allow list approach with all image redaction (#1145)
* Improve process names method in DICOM image redactor (#1150)
* Adding examples of toggling metadata usage and saving bboxes (#1158)
* Updating verification engines to include latest updates to redactor engines (#1162)
* Improved bbox processor (#1163)
* Updating verification engines and enable plotting of custom bboxes (#1164)
* Added image processing class to preprocess the image before running OCR (#1166)
* Added support for Microsoft's document intelligence OCR
  
### Changed
#### Analyzer
* Refactored the `NlpEngine` and Ner recognizers (`SpacyRecognizer`, `TransformersRecognizer`, `StanzaRecognizer`) to allow simpler integration of huggingface and transformers models (#1159). This includes:
    - Changes in how NER results flow through Presidio (see docs)
    - NER/model definition is now defined using a conf file or a `NerModelConfiguration` object.
    - Integrated `spacy-huggingface-pipelines` for a more robust integration of huggingface models.        
* As a result, `SpacyRecognizer` logic has changed, please see #1159. Some fields within the class are now deprecated.
* Updated type checks (#1175)
* Enabled regex flags manipulation (#1193)
  
#### Anonymizer
* Initial logic check for merging 2 entities (#1092)
* Fix Sphinx warning in OperatorConfig (#1143)
* Fix type mismatch in check_label_groups parameter in spacy_recognizer (#1130)
* anonymize_list return type hint fix (#1178)
* 
#### General
* We no longer use Pipenv.lock. Locking happens as part of the CI. (#1152)
* Changed the ACR instance (#1089)
* Updated to Cred Scan V3 (#1154) 

## [2.2.33] - June 1st 2023
### Added
#### Anonymizer
* Added `keep`, an no-op anonymizer that allows preserving some types of PII while keeping track of its position in anonymized output. (#1062)
* Added `BatchAnonymizerEngine` to complement the `BatchAnalyzerEngine` for lists, and dicts (#993)

### General
* Drop support for Python 3.7
* Add support for Python 3.11
* New demo app for Presidio, based on Streamlit (#1054)
* GPT based synthetic data generation (#1051)

## [2.2.32] - 25.01.2023
### Changed
#### General
* Updated dependencies

#### Analyzer
* Fixed exception on whitespace in AU recognizers
* Updated API version for Text Analytics in sample

#### Anonymizer
* Fixed merge entity from the same type

#### Image redactor
* Modified `ImagePiiVerifyEngine` to allow passing of kwargs
* Updated template for building image redactor yaml
* Updated all image redactor engines and OCR classes to allow passing of an OCR confidence threshold and other OCR parameters
* Moved general bounding box operations to new class `BboxProcessor`
* Updated `presidio-image-redactor` version from 0.0.45 to 0.0.46

### Added
#### Analyzer
* Added revised example for transformer recognizer

#### Image redactor
* Added evaluation code for the DICOM image redaction capabilities
* REST API to support web applications payload

#### General
* Updated documentation to include instructions on using DICOM evaluation code
* Updated documentation to mention OCR thresholding

## [2.2.31] - 14.12.2022
### Changed
#### Image-Redactor
* Added DICOM image redaction capabilities (`DicomImageRedactorEngine` class and tests)
* Updated `setup.py` to include new required packages for DICOM capabilities
* Updated Pipfile and Pipfile.lock
* Updated `presidio-image-redactor` version from 0.0.44 to 0.0.45
* Updated the `ImagePiiVerifyEngine` class to allow use of custom analyzer engines

#### General
* Updated `NOTICE` to include licenses of added packages
* Updated docs with getting started code for new `DicomImageRedactorEngine`

## [2.2.30] - 25.10.2022
### Added
#### Analyzer
* Added Italian fiscal code recognizer
* Added Italian driver license recognizer
* Added Italian identity card recognizer
* Added Italian passport recognizer
* Added `TransformersNlpEngine` to support transformer based NER models within spaCy pipelines
* Added pattern for next gen US passport in `presidio-analyzer/presidio_analyzer/predefined_recognizers/us_passport_recognizer.py`

### Changed
#### Analyzer
* Improved MEDICAL_LICENSE pattern and fixed checksum verification
* Bugfix for context handling by aligning results to recognizers using a unique identifier and not recognizer name
* Updated Pipfile.lock

#### Anonymizer
* Removed constraint on empty texts

#### Image-Redactor
* Updated Pipfile.lock

#### General
* Updated `pipenv` version
* Updated `black` and `flake8` in pre-commit scripts
* Updated docs for NLP engine

## [2.2.29] - 12.07.2022
### Added

#### General
- Added Presidio to OSSF (Open Source Security Foundation)
- Added CodeQL scanning

#### Analyzer
- Introduced [BatchAnalyzerEngine](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/batch_analyzer_engine.py)
- Added [allow-list functionality](https://github.com/microsoft/presidio/blob/4cbfc1a80dc15da7d5a9cf5a1c680e8df4f2b349/presidio-analyzer/presidio_analyzer/analyzer_engine.py#L135) to ignore specific strings
- Added notebook on [anonymizing known values](https://github.com/microsoft/presidio/blob/main/docs/samples/python/Anonymizing%20known%20values.ipynb)
- Added [sample for using `transformers` models in Presidio](https://github.com/microsoft/presidio/blob/main/docs/samples/python/transformers_recognizer.py)

### Changed

#### Anonymizer
- Bug fix for getting the text before anonymizing (https://github.com/microsoft/presidio/pull/890)

#### Image redactor
- Deps update

## [2.2.28] - 04.05.2022
### Changed
#### Analyzer
* Improved deny-list regex and customizability
* Added documentation for existing spaCy models
* Bugfix in analysis explanation scores

#### Image redactor
* PIL version updated to 9.0.1

### Added
#### Analyzer
* Recognizers can be loaded from YAML


## [2.2.27] - 08.03.2022
### Changed

#### Analyzer
* Improved context mechanisms to support recognizer level context enhacenement and cross-entity context support

## [2.2.26] - 23.02.2022
### Changed

#### Analyzer
Bug fix in context support

## [2.2.25] - 21.02.2022
### Changed

#### Analyzer

* Added a URL recognizer
* Added a new capability for creating new logic for context detection. See [ContextAwareEnhancer](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/context_aware_enhancers/context_aware_enhancer.py) and [LemmaContextAwareEnhancer](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/context_aware_enhancers/lemma_context_aware_enhancer.py). Documentation would be added on a future release.
Furthermore, it is now possible to pass context words thruogh the `analyze` method (or via API) and those would be taken into account for context enhancement. 



#### Anonymizer

* Bug fix for entities at the end of a sentence.

#### Docs

- Formatted (black/flake8) the Python examples.

### Removed

#### Analyzer

* Removed the DOMAIN_NAME recognizer. This change means that the `DOMAIN_NAME` entity is no longer returned by Presidio. `URL` would be returned instead, and would catch full addresses and not just domain names (`https://www.microsoft.com/a/b.html` and not just `www.microsoft.com`)



## [2.2.24] - 23.01.2022
### Changed
* Fixed issue when IBAN followed by all caps can't be recognized
* Updated dependencies in Pipfile.lock
* Removed official Python 3.6 support and added support for 3.10
* Added docs for creating a streamlit app
* Added docs for using Flair

### Removed

### Deprecated

## [2.2.23] - 16.11.2021
### Changed
#### Analyzer:
* Added multi-regional phone number recognizer.
* Fixed duplicated entities removal.
* Added sample for structured / semi-structured data in batch.
* Dependencies version bumps.

#### Anonymizer:
* Added sample for getting an identified entity value using a custom Operator.
* Changed packages/imports .
* Added repr to classes.
* Added encryption and decryption samples.
* Remove AnonymizerResult in favor of OperatorResult, for an easier anonymization-deanonymization.
* Anonymizaer and Deanonymizaer to return `operator_name` instead of `operator` in OperatorResult.

## [2.2.2] - 09.06.2021
### Changed
#### Analyzer:
* Databricks based template in Azure Data Factory docs
* Adding ORGANIZATION recognizer docs
* Bumped pydantic from 1.7.3 to 1.7.4
* Updated call to stanza via spacy-stanza
* Added DATE_TIME recognizer
* Added Medical Licence recognizer
* Bumped spacy from 3.0.5 to 3.0.6

## [2.2.1] - 10.05.2021
### Changed
#### Analyzer:
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

[unreleased]: https://github.com/microsoft/presidio/compare/2.2.353...HEAD
[2.2.353]: https://github.com/microsoft/presidio/compare/2.2.352...2.2.353
[2.2.352]: https://github.com/microsoft/presidio/compare/2.2.351...2.2.352
[2.2.351]: https://github.com/microsoft/presidio/compare/2.2.350...2.2.351
[2.2.350]: https://github.com/microsoft/presidio/compare/2.2.35...2.2.350
[2.2.35]: https://github.com/microsoft/presidio/compare/2.2.34...2.2.35
[2.2.34]: https://github.com/microsoft/presidio/compare/2.2.33...2.2.34
[2.2.33]: https://github.com/microsoft/presidio/compare/2.2.32...2.2.33
[2.2.32]: https://github.com/microsoft/presidio/compare/2.2.31...2.2.32
[2.2.31]: https://github.com/microsoft/presidio/compare/2.2.30...2.2.31
[2.2.30]: https://github.com/microsoft/presidio/compare/2.2.29...2.2.30
[2.2.29]: https://github.com/microsoft/presidio/compare/2.2.28...2.2.29
[2.2.28]: https://github.com/microsoft/presidio/compare/2.2.27...2.2.28
[2.2.27]: https://github.com/microsoft/presidio/compare/2.2.26...2.2.27
[2.2.26]: https://github.com/microsoft/presidio/compare/2.2.25...2.2.26
[2.2.25]: https://github.com/microsoft/presidio/compare/2.2.24...2.2.25
[2.2.24]: https://github.com/microsoft/presidio/compare/2.2.23...2.2.24
[2.2.23]: https://github.com/microsoft/presidio/compare/2.2.2...2.2.23
[2.2.2]: https://github.com/microsoft/presidio/compare/2.2.1...2.2.2
[2.2.1]: https://github.com/microsoft/presidio/compare/2.2.0...2.2.1
