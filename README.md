# Repository Coverage (presidio-structured)

[Full report](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-structured/htmlcov/index.html)

| Name                                                |    Stmts |     Miss |   Cover |   Missing |
|---------------------------------------------------- | -------: | -------: | ------: | --------: |
| presidio\_structured/\_\_init\_\_.py                |        7 |        0 |    100% |           |
| presidio\_structured/analysis\_builder.py           |      119 |       13 |     89% |64, 78-86, 134-137, 193-197, 373 |
| presidio\_structured/config/\_\_init\_\_.py         |        2 |        0 |    100% |           |
| presidio\_structured/config/structured\_analysis.py |        4 |        0 |    100% |           |
| presidio\_structured/data/\_\_init\_\_.py           |        3 |        0 |    100% |           |
| presidio\_structured/data/data\_processors.py       |       93 |       19 |     80% |51, 146-149, 156, 170-179, 206-207, 212-216 |
| presidio\_structured/data/data\_reader.py           |       17 |        5 |     71% |26, 47, 68-70 |
| presidio\_structured/structured\_engine.py          |       26 |        2 |     92% |     66-67 |
|                                           **TOTAL** |  **271** |   **39** | **86%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-structured/badge.svg)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-structured/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-structured/endpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-structured/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fcoverage-data-presidio-structured%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-structured/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.