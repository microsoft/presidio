# Recipes Gallery

This directory contains the Presidio Recipes Gallery, a collection of curated, domain-specific examples showing how to customize Presidio for different data privacy scenarios.

## Directory Structure

```
recipes/
├── README.md                  # This file
├── index.md                   # Main recipes gallery page
├── CONTRIBUTING.md            # Guidelines for contributing new recipes
├── template.md                # Template for creating new recipes
└── [future recipe folders]/   # Individual recipe implementations
```

## Quick Links

- **Browse Recipes**: See [index.md](index.md) for the recipes gallery homepage
- **Contribute**: Read [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines
- **Create a Recipe**: Use [template.md](template.md) as a starting point

## What's Next?

This scaffolding provides the foundation for the recipes gallery. Future recipes will be added as subdirectories, each containing:

- An `index.md` overview page
- A Jupyter notebook (`recipe.ipynb`) with the full implementation
- Any supporting files (data generators, custom recognizers, etc.)

Example future structure:
```
recipes/
├── financial-chatbot/
│   ├── index.md
│   ├── recipe.ipynb
│   └── data_generator.py
├── clinical-notes/
│   ├── index.md
│   └── recipe.ipynb
└── ...
```

## For Maintainers

When adding a new recipe:

1. Create a subdirectory under `recipes/` with a descriptive name
2. Add the recipe files following the template structure
3. Update `recipes/index.md` to link to the new recipe
4. Add the recipe to `mkdocs.yml` navigation if it should appear in the main menu
5. Test the recipe notebook to ensure it runs correctly

## Documentation

The recipes gallery is part of the main Presidio documentation site built with MkDocs. Changes to files in this directory will be reflected in the published documentation at https://microsoft.github.io/presidio/recipes/
