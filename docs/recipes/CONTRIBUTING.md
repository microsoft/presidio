# Contributing to Presidio Recipes Gallery

Thank you for your interest in contributing to the Presidio Recipes Gallery! Community-contributed recipes help other users learn how to customize Presidio for specific domains and use cases.

## What Makes a Good Recipe?

A valuable recipe should:

1. **Address a Specific Domain**: Focus on a well-defined scenario (e.g., "Financial chatbot conversations with credit card and account numbers" rather than generic "text processing")

2. **Be Reproducible**: Include all code, data generation methods, and configuration needed for others to replicate your results

3. **Provide Performance Context**: Include evaluation metrics (precision, recall, F₂ score, latency) so users can assess if the approach meets their needs

4. **Show Progressive Complexity**: Demonstrate multiple implementation levels, such as:
   - Out-of-the-box Presidio with default recognizers
   - Enhanced configuration with custom recognizers or deny-lists
   - Advanced approaches using custom models, transformers, or LLMs

5. **Include Clear Documentation**: Explain design decisions, trade-offs, and when each approach is most appropriate

## Recipe Structure

Each recipe should follow this structure:

### 1. Scenario Description
- **Domain**: Healthcare, Finance, Retail, etc.
- **Data Type**: Chat logs, clinical notes, JSON API responses, etc.
- **Privacy Requirements**: Which PII types need detection and anonymization
- **Constraints**: Performance requirements, accuracy thresholds, computational limits

### 2. Synthetic Data Generation
- Script or method to create representative test data
- Explanation of data characteristics (entity frequency, context patterns, edge cases)
- Sample data showing realistic examples

### 3. Configuration Levels
For each level, provide:
- Configuration code (YAML and/or Python)
- Custom recognizers if applicable
- Model selection and NLP engine setup
- Any preprocessing or postprocessing steps

### 4. Evaluation Results
For each configuration level:
- **Precision**: How many detected entities were correct?
- **Recall**: How many actual PII entities were detected?
- **F₂ Score**: Recall-weighted harmonic mean (useful when missing PII is more costly than false positives)
- **Latency**: Average processing time per sample
- Confusion matrix or error analysis (optional but helpful)

### 5. Jupyter Notebook
- Interactive notebook with complete implementation
- Clear markdown cells explaining each step
- Outputs visible so users can review without running
- Requirements section listing all dependencies

### 6. Recommendations
- When to use each configuration level
- Trade-offs between accuracy and performance
- Tips for adapting to similar use cases
- Known limitations or edge cases

## Submission Process

### Before You Start

1. **Check Existing Recipes**: Review current recipes to avoid duplication
2. **Open an Issue**: Propose your recipe idea in a GitHub issue to get feedback before investing significant effort
3. **Review Guidelines**: Read the main [CONTRIBUTING.md](../../CONTRIBUTING.md) for general contribution requirements

### Creating Your Recipe

1. **Fork the Repository**: Create a fork of [microsoft/presidio](https://github.com/microsoft/presidio)

2. **Create Recipe Files**: Add your files under `docs/recipes/<your-recipe-name>/`:
   ```
   docs/recipes/your-recipe-name/
   ├── index.md                    # Overview and results
   ├── recipe.ipynb               # Jupyter notebook with full implementation
   ├── data_generator.py          # Script to generate synthetic data (if applicable)
   ├── requirements.txt           # Python dependencies (if beyond standard Presidio)
   └── README.md                  # Quick reference (optional)
   ```

3. **Use the Template**: Start with our [recipe template](template.md) to ensure consistency

4. **Write Your Notebook**: 
   - Include all imports and setup code
   - Add markdown explanations between code cells
   - Show outputs so users can review results
   - Test that the notebook runs end-to-end in a clean environment

5. **Document Results**: Create clear visualizations or tables showing performance metrics

### Submitting Your Recipe

1. **Create a Pull Request**: Submit your recipe as a PR to the main repository

2. **Link to Your Issue**: Reference the issue where you proposed the recipe

3. **Complete the PR Template**: Provide:
   - Description of the scenario and domain
   - Summary of key findings
   - Any special requirements or dependencies
   - Confirmation that you've tested the notebook

4. **Update Navigation**: Add your recipe to `mkdocs.yml` and update `docs/recipes/index.md` with a link and brief description

5. **Address Review Feedback**: Maintainers will review and may request changes

## Recipe Checklist

Before submitting, ensure your recipe includes:

- [ ] Clear scenario description with domain context
- [ ] Method for generating or obtaining test data
- [ ] At least 2 different configuration levels (e.g., out-of-the-box and custom)
- [ ] Evaluation metrics for each configuration (precision, recall, F₂, latency)
- [ ] Working Jupyter notebook with visible outputs
- [ ] Documentation explaining design decisions and trade-offs
- [ ] Requirements file listing dependencies
- [ ] Notebook tested in a clean environment
- [ ] Entry added to recipes gallery index
- [ ] Entry added to mkdocs.yml navigation

## Code Quality Standards

Recipes should follow the same quality standards as other Presidio contributions:

- **Code Style**: Follow Python conventions (PEP 8)
- **Linting**: Code should pass `ruff check .` without errors
- **Documentation**: Include docstrings for any custom functions
- **Testing**: If introducing new recognizers, include unit tests
- **Dependencies**: Minimize external dependencies; document any required

## Example Data Guidelines

When creating synthetic data:

- **Realistic**: Data should resemble actual use cases in the domain
- **Diverse**: Include various PII types, contexts, and edge cases
- **Safe**: Never include real PII or sensitive information
- **Reproducible**: Use fixed random seeds or provide generation scripts
- **Labeled**: If providing evaluation data, include ground truth labels

## Performance Benchmarking

When reporting performance metrics:

- **Environment**: Document hardware specs (CPU, memory, GPU if used)
- **Sample Size**: Report number of samples in evaluation dataset
- **Methodology**: Explain how ground truth was established
- **Reproducibility**: Include code to reproduce evaluation
- **Statistical Significance**: For small datasets, report confidence intervals if possible

## Types of Recipes We're Looking For

High-priority domains:
- **Healthcare**: Clinical notes, radiology reports, patient correspondence
- **Financial Services**: Transaction logs, customer service chats, loan applications
- **Retail/E-commerce**: Customer reviews, support tickets, order data
- **Enterprise**: Email archives, HR documents, internal communications
- **Social Media**: User-generated content, chat logs, forum posts
- **Legal**: Contracts, court documents, legal correspondence
- **Education**: Student records, academic papers, learning management systems
- **Multilingual**: Non-English scenarios (Spanish, French, German, Chinese, etc.)

## Getting Help

If you need assistance creating a recipe:

- **Discussion**: Start a discussion in the [GitHub Discussions](https://github.com/microsoft/presidio/discussions) area
- **Email**: Contact [presidio@microsoft.com](mailto:presidio@microsoft.com)
- **Issues**: Ask questions in your proposal issue
- **Examples**: Review existing recipes and samples for guidance

## License

By contributing a recipe, you agree to license your contribution under the same [MIT License](../../LICENSE) as the Presidio project.

## Recognition

Contributors of accepted recipes will be:
- Credited in the recipe documentation
- Listed in the project's contributors
- Mentioned in release notes when the recipe is published

Thank you for helping make Presidio more accessible and useful for the community!
