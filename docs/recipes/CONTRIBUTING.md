# Contributing to Presidio Recipes Gallery

Thank you for your interest in contributing! Recipes help others learn how to customize Presidio for specific domains.

## What Makes a Good Recipe?

A good recipe should:

1. **Focus on a Specific Domain**: Target a well-defined scenario (e.g., "Financial chatbot logs", "Clinical notes", "Customer support tickets")

2. **Be Reproducible**: Include working code that others can run

3. **Follow the Research Pattern**: Build upon the end-to-end approach from [presidio-research](https://github.com/microsoft/presidio-research), showing:
   - **Data Synthesis**: How to generate or obtain test data
   - **Configuration**: Your Presidio setup with any custom recognizers
   - **Evaluation**: Metrics (precision, recall, F₂) showing performance

4. **Keep It Simple**: Focus on getting a working example first. Detailed documentation can come later.

## Recipe Format

### Option 1: Jupyter Notebook (Recommended)

The easiest way to contribute is with a Jupyter notebook that follows the presidio-research pattern:

```
your-recipe-name/
├── recipe.ipynb          # Main notebook with data synthesis → evaluation
└── README.md             # Brief overview (optional)
```

Your notebook should include:
- **Data Synthesis**: Generate synthetic data for your scenario
- **Presidio Configuration**: Show your setup (default, custom recognizers, or custom models)
- **Evaluation**: Measure and report precision, recall, F₂ score, latency
- **Key Findings**: Brief summary of results and when to use this approach

### Option 2: Python Scripts

If you prefer scripts over notebooks:

```
your-recipe-name/
├── synthesize_data.py    # Generate test data
├── configure.py          # Presidio setup
├── evaluate.py           # Run evaluation
└── README.md             # Overview and instructions
```

## Quick Contribution Steps

1. **Fork the repo** and create a new branch

2. **Create your recipe folder** under `docs/recipes/your-recipe-name/`

3. **Use the template**: Copy `template.md` or start with a notebook

4. **Focus on working code first**: Don't worry about making it perfect

5. **Submit a PR**: We'll help refine it during review

## Evaluation Metrics

Include at minimum:
- **Precision**: Percentage of detected entities that were correct
- **Recall**: Percentage of actual PII that was detected  
- **F₂ Score**: Recall-weighted F-score (emphasizes catching all PII)
- **Latency**: Average processing time per sample

## Examples to Learn From

- [Presidio Research](https://github.com/microsoft/presidio-research): Reference repository with evaluation tools
- [Presidio Samples](../samples/index.md): Additional examples and patterns

## Questions?

- Open an issue with the `recipe` label
- Email [presidio@microsoft.com](mailto:presidio@microsoft.com)
- Tag @omri374 in your PR for guidance

## License

By contributing, you agree to license your work under the MIT License.
