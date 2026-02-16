# Repository Coverage (presidio-image-redactor)

[Full report](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-image-redactor/htmlcov/index.html)

| Name                                                            |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| presidio\_image\_redactor/\_\_init\_\_.py                       |       14 |        0 |    100% |           |
| presidio\_image\_redactor/bbox.py                               |       75 |       10 |     87% |81, 87-88, 92, 104, 125-136, 165-167 |
| presidio\_image\_redactor/dicom\_image\_pii\_verify\_engine.py  |       95 |        1 |     99% |        99 |
| presidio\_image\_redactor/dicom\_image\_redactor\_engine.py     |      381 |       24 |     94% |64-67, 182, 250, 309-310, 331, 368-373, 531-532, 540, 722, 728, 769, 893, 1020-1021, 1054 |
| presidio\_image\_redactor/document\_intelligence\_ocr.py        |       58 |       12 |     79% |132-145, 155-156 |
| presidio\_image\_redactor/entities/\_\_init\_\_.py              |        3 |        0 |    100% |           |
| presidio\_image\_redactor/entities/api\_request\_convertor.py   |       34 |        4 |     88% |     61-64 |
| presidio\_image\_redactor/entities/image\_recognizer\_result.py |       18 |        1 |     94% |        52 |
| presidio\_image\_redactor/entities/invalid\_exception.py        |        4 |        0 |    100% |           |
| presidio\_image\_redactor/image\_analyzer\_engine.py            |      186 |       23 |     88% |62, 68, 96, 236-250, 265-275, 287-289, 408-409 |
| presidio\_image\_redactor/image\_pii\_verify\_engine.py         |       30 |        8 |     73% |13-17, 64, 77, 92 |
| presidio\_image\_redactor/image\_processing\_engine.py          |      121 |       17 |     86% |63-73, 81-83, 302, 307, 312, 367-370 |
| presidio\_image\_redactor/image\_redactor\_engine.py            |       39 |        2 |     95% |    24, 65 |
| presidio\_image\_redactor/ocr.py                                |       10 |        1 |     90% |        16 |
| presidio\_image\_redactor/tesseract\_ocr.py                     |        6 |        0 |    100% |           |
| **TOTAL**                                                       | **1074** |  **103** | **90%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-image-redactor/badge.svg)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-image-redactor/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-image-redactor/endpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-image-redactor/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fcoverage-data-presidio-image-redactor%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-image-redactor/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.