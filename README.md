# Repository Coverage (presidio-analyzer)

[Full report](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-analyzer/htmlcov/index.html)

| Name                                                                                                             |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| presidio\_analyzer/\_\_init\_\_.py                                                                               |       25 |        0 |    100% |           |
| presidio\_analyzer/analysis\_explanation.py                                                                      |       26 |        4 |     85% | 54-57, 65 |
| presidio\_analyzer/analyzer\_engine.py                                                                           |      130 |        4 |     97% |74, 232-233, 384 |
| presidio\_analyzer/analyzer\_engine\_provider.py                                                                 |       64 |        8 |     88% |     54-64 |
| presidio\_analyzer/analyzer\_request.py                                                                          |       19 |       14 |     26% |     25-40 |
| presidio\_analyzer/app\_tracer.py                                                                                |        8 |        2 |     75% |     26-27 |
| presidio\_analyzer/batch\_analyzer\_engine.py                                                                    |       52 |        1 |     98% |        24 |
| presidio\_analyzer/context\_aware\_enhancers/\_\_init\_\_.py                                                     |        3 |        0 |    100% |           |
| presidio\_analyzer/context\_aware\_enhancers/context\_aware\_enhancer.py                                         |       17 |        1 |     94% |        66 |
| presidio\_analyzer/context\_aware\_enhancers/lemma\_context\_aware\_enhancer.py                                  |       96 |        8 |     92% |83-84, 101-105, 120-121, 167, 270 |
| presidio\_analyzer/dict\_analyzer\_result.py                                                                     |        5 |        0 |    100% |           |
| presidio\_analyzer/entity\_recognizer.py                                                                         |       66 |        4 |     94% |88, 133, 141, 182 |
| presidio\_analyzer/llm\_utils/\_\_init\_\_.py                                                                    |        6 |        0 |    100% |           |
| presidio\_analyzer/llm\_utils/config\_loader.py                                                                  |       45 |        4 |     91% |26, 46, 121-122 |
| presidio\_analyzer/llm\_utils/entity\_mapper.py                                                                  |       71 |        0 |    100% |           |
| presidio\_analyzer/llm\_utils/examples\_loader.py                                                                |       18 |        0 |    100% |           |
| presidio\_analyzer/llm\_utils/langextract\_helper.py                                                             |       61 |        6 |     90% |11-12, 135, 143, 165-166 |
| presidio\_analyzer/llm\_utils/prompt\_loader.py                                                                  |       19 |        2 |     89% |     53-54 |
| presidio\_analyzer/lm\_recognizer.py                                                                             |       48 |        1 |     98% |        49 |
| presidio\_analyzer/local\_recognizer.py                                                                          |        3 |        0 |    100% |           |
| presidio\_analyzer/nlp\_engine/\_\_init\_\_.py                                                                   |        8 |        0 |    100% |           |
| presidio\_analyzer/nlp\_engine/ner\_model\_configuration.py                                                      |       46 |        2 |     96% |  117, 120 |
| presidio\_analyzer/nlp\_engine/nlp\_artifacts.py                                                                 |       30 |        0 |    100% |           |
| presidio\_analyzer/nlp\_engine/nlp\_engine.py                                                                    |       22 |        2 |     91% |    60, 65 |
| presidio\_analyzer/nlp\_engine/nlp\_engine\_provider.py                                                          |       90 |        4 |     96% |100, 107, 165, 198 |
| presidio\_analyzer/nlp\_engine/spacy\_nlp\_engine.py                                                             |      111 |        9 |     92% |78, 83, 99, 140, 144, 185, 243, 267, 273 |
| presidio\_analyzer/nlp\_engine/stanza\_nlp\_engine.py                                                            |      188 |       20 |     89% |12-13, 210, 212, 227-231, 296, 318-319, 351, 361-362, 388-389, 393, 416, 419 |
| presidio\_analyzer/nlp\_engine/transformers\_nlp\_engine.py                                                      |       47 |        3 |     94% |     10-12 |
| presidio\_analyzer/pattern.py                                                                                    |       19 |        2 |     89% |    42, 46 |
| presidio\_analyzer/pattern\_recognizer.py                                                                        |       93 |        8 |     91% |210, 256-264 |
| presidio\_analyzer/predefined\_recognizers/\_\_init\_\_.py                                                       |       51 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/\_\_init\_\_.py                                     |        0 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/australia/\_\_init\_\_.py                           |        5 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/australia/au\_abn\_recognizer.py                    |       20 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/australia/au\_acn\_recognizer.py                    |       20 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/australia/au\_medicare\_recognizer.py               |       19 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/australia/au\_tfn\_recognizer.py                    |       19 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/finland/\_\_init\_\_.py                             |        2 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/finland/fi\_personal\_identity\_code\_recognizer.py |       23 |        1 |     96% |        54 |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/\_\_init\_\_.py                               |        7 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/in\_aadhaar\_recognizer.py                    |       35 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/in\_gstin\_recognizer.py                      |       54 |        5 |     91% |124, 129, 138, 164, 168 |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/in\_pan\_recognizer.py                        |       10 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/in\_passport\_recognizer.py                   |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/in\_vehicle\_registration\_recognizer.py      |       87 |        3 |     97% |   383-391 |
| presidio\_analyzer/predefined\_recognizers/country\_specific/india/in\_voter\_recognizer.py                      |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/italy/\_\_init\_\_.py                               |        6 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/italy/it\_driver\_license\_recognizer.py            |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/italy/it\_fiscal\_code\_recognizer.py               |       29 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/italy/it\_identity\_card\_recognizer.py             |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/italy/it\_passport\_recognizer.py                   |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/italy/it\_vat\_code.py                              |       28 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/korea/\_\_init\_\_.py                               |        2 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/korea/kr\_rrn\_recognizer.py                        |       26 |        2 |     92% |    89, 93 |
| presidio\_analyzer/predefined\_recognizers/country\_specific/poland/\_\_init\_\_.py                              |        2 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/poland/pl\_pesel\_recognizer.py                     |       15 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/singapore/\_\_init\_\_.py                           |        3 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/singapore/sg\_fin\_recognizer.py                    |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/singapore/sg\_uen\_recognizer.py                    |       52 |        4 |     92% |115, 150, 172, 177 |
| presidio\_analyzer/predefined\_recognizers/country\_specific/spain/\_\_init\_\_.py                               |        3 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/spain/es\_nie\_recognizer.py                        |       20 |        1 |     95% |        69 |
| presidio\_analyzer/predefined\_recognizers/country\_specific/spain/es\_nif\_recognizer.py                        |       16 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/thai/\_\_init\_\_.py                                |        2 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/thai/th\_tnin\_recognizer.py                        |       28 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/uk/\_\_init\_\_.py                                  |        3 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/uk/uk\_nhs\_recognizer.py                           |       16 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/uk/uk\_nino\_recognizer.py                          |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/\_\_init\_\_.py                                  |        8 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/aba\_routing\_recognizer.py                      |       19 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/medical\_license\_recognizer.py                  |       25 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/us\_bank\_recognizer.py                          |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/us\_driver\_license\_recognizer.py               |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/us\_itin\_recognizer.py                          |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/us\_passport\_recognizer.py                      |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/country\_specific/us/us\_ssn\_recognizer.py                           |       26 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/\_\_init\_\_.py                                               |        8 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/credit\_card\_recognizer.py                                   |       25 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/crypto\_recognizer.py                                         |       78 |        7 |     91% |71, 111, 119, 123, 125, 130, 139 |
| presidio\_analyzer/predefined\_recognizers/generic/date\_recognizer.py                                           |        9 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/email\_recognizer.py                                          |       13 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/iban\_patterns.py                                             |       17 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/iban\_recognizer.py                                           |       80 |        6 |     92% |95, 97-99, 148, 205 |
| presidio\_analyzer/predefined\_recognizers/generic/ip\_recognizer.py                                             |       15 |        2 |     87% |     62-63 |
| presidio\_analyzer/predefined\_recognizers/generic/phone\_recognizer.py                                          |       34 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/generic/url\_recognizer.py                                            |       10 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/ner/\_\_init\_\_.py                                                   |        2 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/ner/gliner\_recognizer.py                                             |       52 |        8 |     85% |14-16, 63, 70-74, 105, 165 |
| presidio\_analyzer/predefined\_recognizers/nlp\_engine\_recognizers/\_\_init\_\_.py                              |        4 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/nlp\_engine\_recognizers/spacy\_recognizer.py                         |       40 |        2 |     95% |   57, 137 |
| presidio\_analyzer/predefined\_recognizers/nlp\_engine\_recognizers/stanza\_recognizer.py                        |        5 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/nlp\_engine\_recognizers/transformers\_recognizer.py                  |        8 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/third\_party/\_\_init\_\_.py                                          |        4 |        0 |    100% |           |
| presidio\_analyzer/predefined\_recognizers/third\_party/ahds\_recognizer.py                                      |       61 |       28 |     54% |18-27, 64, 71, 109, 122-149, 153-161 |
| presidio\_analyzer/predefined\_recognizers/third\_party/azure\_ai\_language.py                                   |       60 |       17 |     72% |9-11, 55, 66, 75, 91-109, 135, 137 |
| presidio\_analyzer/predefined\_recognizers/third\_party/langextract\_recognizer.py                               |       34 |        1 |     97% |        52 |
| presidio\_analyzer/predefined\_recognizers/third\_party/ollama\_langextract\_recognizer.py                       |       23 |        0 |    100% |           |
| presidio\_analyzer/recognizer\_registry/\_\_init\_\_.py                                                          |        3 |        0 |    100% |           |
| presidio\_analyzer/recognizer\_registry/recognizer\_registry.py                                                  |      114 |       15 |     87% |125, 155, 158, 208, 290-291, 306-309, 312-316, 328 |
| presidio\_analyzer/recognizer\_registry/recognizer\_registry\_provider.py                                        |       61 |        1 |     98% |       166 |
| presidio\_analyzer/recognizer\_registry/recognizers\_loader\_utils.py                                            |      124 |        7 |     94% |23, 39, 118, 200, 338-339, 353 |
| presidio\_analyzer/recognizer\_result.py                                                                         |       57 |        5 |     91% |59-60, 102-106 |
| presidio\_analyzer/remote\_recognizer.py                                                                         |       15 |        2 |     87% |    50, 54 |
|                                                                                                        **TOTAL** | **3172** |  **226** | **93%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-analyzer/badge.svg)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-analyzer/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-analyzer/endpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-analyzer/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fcoverage-data-presidio-analyzer%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-analyzer/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.