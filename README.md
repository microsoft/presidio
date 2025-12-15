# Repository Coverage (presidio-cli)

[Full report](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-cli/htmlcov/index.html)

| Name                          |    Stmts |     Miss |   Cover |   Missing |
|------------------------------ | -------: | -------: | ------: | --------: |
| presidio\_cli/\_\_init\_\_.py |        8 |        2 |     75% |       7-8 |
| presidio\_cli/\_\_main\_\_.py |        3 |        3 |      0% |       1-4 |
| presidio\_cli/analyzer.py     |       49 |        1 |     98% |       101 |
| presidio\_cli/cli.py          |      137 |       20 |     85% |86-93, 116-117, 121, 223-225, 227, 232-234, 237, 245-247, 255-257, 266 |
| presidio\_cli/config.py       |       85 |        4 |     95% |104, 118-119, 163 |
| **TOTAL**                     |  **282** |   **30** | **89%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-cli/badge.svg)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-cli/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/microsoft/presidio/coverage-data-presidio-cli/endpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-cli/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fcoverage-data-presidio-cli%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/microsoft/presidio/blob/coverage-data-presidio-cli/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.