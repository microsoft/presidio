## General pipenv instructions
Pipenv documentation: https://pipenv.readthedocs.io/en/latest/

Useful Pipenv commands:
```
$ pipenv -h
```

General flow for adding a new dependency:
1. Manually add dependency name to Pipfile.
2. Create a new Pipfile.lock and update environment:
```
$ pipenv update --sequential
```

    `pipenv update` runs the `lock` command as well as the `sync` command which installs all requirements in the lock file into the current virtual environment. `--sequential` installs the dependencies sequentially to increase reproducibility.