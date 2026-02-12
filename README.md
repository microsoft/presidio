# Repository Coverage (presidio-anonymizer)

[Full report](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-anonymizer/htmlcov/index.html)

| Name                                                             |    Stmts |     Miss |   Cover |   Missing |
|----------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| presidio\_anonymizer/\_\_init\_\_.py                             |        7 |        0 |    100% |           |
| presidio\_anonymizer/anonymizer\_engine.py                       |       95 |        0 |    100% |           |
| presidio\_anonymizer/batch\_anonymizer\_engine.py                |       31 |        0 |    100% |           |
| presidio\_anonymizer/core/\_\_init\_\_.py                        |        3 |        0 |    100% |           |
| presidio\_anonymizer/core/engine\_base.py                        |       44 |        1 |     98% |       116 |
| presidio\_anonymizer/core/text\_replace\_builder.py              |       23 |        0 |    100% |           |
| presidio\_anonymizer/deanonymize\_engine.py                      |       18 |        0 |    100% |           |
| presidio\_anonymizer/entities/\_\_init\_\_.py                    |        9 |        0 |    100% |           |
| presidio\_anonymizer/entities/conflict\_resolution\_strategy.py  |        4 |        0 |    100% |           |
| presidio\_anonymizer/entities/engine/\_\_init\_\_.py             |        4 |        0 |    100% |           |
| presidio\_anonymizer/entities/engine/dict\_recognizer\_result.py |        5 |        0 |    100% |           |
| presidio\_anonymizer/entities/engine/operator\_config.py         |       24 |        1 |     96% |        27 |
| presidio\_anonymizer/entities/engine/pii\_entity.py              |       27 |        2 |     93% |    25, 37 |
| presidio\_anonymizer/entities/engine/recognizer\_result.py       |       41 |        0 |    100% |           |
| presidio\_anonymizer/entities/engine/result/\_\_init\_\_.py      |        3 |        0 |    100% |           |
| presidio\_anonymizer/entities/engine/result/engine\_result.py    |       25 |        0 |    100% |           |
| presidio\_anonymizer/entities/engine/result/operator\_result.py  |       23 |        1 |     96% |        23 |
| presidio\_anonymizer/entities/invalid\_exception.py              |        4 |        0 |    100% |           |
| presidio\_anonymizer/operators/\_\_init\_\_.py                   |       21 |        3 |     86% |     19-21 |
| presidio\_anonymizer/operators/aes\_cipher.py                    |       28 |        0 |    100% |           |
| presidio\_anonymizer/operators/ahds\_surrogate.py                |      103 |       40 |     61% |9, 224, 232, 236, 279, 281, 283-284, 288-313, 325-332, 336-340, 344-362 |
| presidio\_anonymizer/operators/custom.py                         |       18 |        0 |    100% |           |
| presidio\_anonymizer/operators/deanonymize\_keep.py              |        7 |        1 |     86% |        18 |
| presidio\_anonymizer/operators/decrypt.py                        |       18 |        0 |    100% |           |
| presidio\_anonymizer/operators/encrypt.py                        |       26 |        1 |     96% |        48 |
| presidio\_anonymizer/operators/hash.py                           |       34 |        0 |    100% |           |
| presidio\_anonymizer/operators/keep.py                           |       13 |        1 |     92% |        38 |
| presidio\_anonymizer/operators/mask.py                           |       33 |        0 |    100% |           |
| presidio\_anonymizer/operators/operator.py                       |       20 |        4 |     80% |24, 29, 34, 39 |
| presidio\_anonymizer/operators/operators\_factory.py             |       56 |        4 |     93% |65-72, 157 |
| presidio\_anonymizer/operators/redact.py                         |       11 |        0 |    100% |           |
| presidio\_anonymizer/operators/replace.py                        |       17 |        0 |    100% |           |
| presidio\_anonymizer/services/\_\_init\_\_.py                    |        0 |        0 |    100% |           |
| presidio\_anonymizer/services/app\_entities\_convertor.py        |       20 |        0 |    100% |           |
| presidio\_anonymizer/services/validators.py                      |       26 |        0 |    100% |           |
| **TOTAL**                                                        |  **841** |   **59** | **93%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-anonymizer/badge.svg)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-anonymizer/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-anonymizer/endpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-anonymizer/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fcoverage-data-presidio-anonymizer%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-anonymizer/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.