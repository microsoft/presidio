# Recipe Template: [Recipe Name]

> **Note**: This is a simplified template for contributing recipes. Focus on providing a working example - detailed documentation can come later.

## Overview

**Domain**: [e.g., Healthcare, Finance, Retail]  
**Data Type**: [e.g., Clinical notes, Chat logs, API responses]  
**Goal**: [What you're trying to detect and anonymize]

## Quick Start

### Sample Data

```python
# Example data that demonstrates the scenario
sample_text = """
[Your example text with PII]
"""
```

### Basic Configuration

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Your Presidio configuration
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Analyze and anonymize
results = analyzer.analyze(text=sample_text, language="en")
anonymized = anonymizer.anonymize(text=sample_text, analyzer_results=results)

print(anonymized.text)
```

## Approach

Describe your approach in a few sentences. What recognizers, models, or techniques did you use?

## Results

**Precision**: [0.XX]  
**Recall**: [0.XX]  
**F₂ Score**: [0.XX]  
**Latency**: [XX ms/sample]

### Key Findings

- [Main insight 1]
- [Main insight 2]
- [Main insight 3]

## Jupyter Notebook (Recommended)

For the complete end-to-end example including data synthesis, configuration, and evaluation, provide a Jupyter notebook (e.g., `recipe.ipynb`).

The notebook should follow the pattern from [presidio-research](https://github.com/microsoft/presidio-research) and include:

1. **Data Synthesis**: Generate synthetic data for your scenario
2. **Configuration**: Set up Presidio with your custom recognizers or models
3. **Evaluation**: Measure precision, recall, and F₂ score
4. **Analysis**: Discuss results and trade-offs

Alternatively, you can provide Python scripts if you prefer.

## Tips for Others

- [Tip 1: When this approach works best]
- [Tip 2: Common pitfalls to avoid]
- [Tip 3: How to adapt to similar scenarios]

---

**Author**: [Your Name]  
**Date**: [YYYY-MM-DD]
