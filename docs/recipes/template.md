# Recipe Template: [Recipe Name]

> **Note**: This is a template for creating new recipes. Replace the bracketed placeholders with your specific content.

## Scenario Description

### Domain
[e.g., Healthcare, Financial Services, Retail, Enterprise, etc.]

### Data Type
[e.g., Clinical notes, Chat conversations, JSON REST API logs, Email archives, etc.]

### Privacy Requirements
[Describe which PII types need to be detected and anonymized, and why]

**Key PII Types**:
- [PII_TYPE_1]: [Context and importance]
- [PII_TYPE_2]: [Context and importance]
- [PII_TYPE_3]: [Context and importance]

### Business Context
[Explain the real-world scenario and why PII protection is needed]

### Constraints
- **Accuracy Requirements**: [e.g., "Must detect 95% of credit card numbers"]
- **Performance Requirements**: [e.g., "Must process 1000 records/minute"]
- **Computational Constraints**: [e.g., "CPU-only environment"]
- **Other Requirements**: [e.g., "Must support real-time processing"]

## Synthetic Data Generation

### Data Characteristics
[Describe the key features of the data that impact PII detection]
- **Entity Density**: [How many PII entities per document on average]
- **Context Patterns**: [Common phrases or structures around PII]
- **Edge Cases**: [Unusual formats, abbreviations, or variations]
- **Language**: [Primary language and any multilingual considerations]

### Sample Data

```
[Include 2-3 representative examples of synthetic data]

Example 1:
"Patient John Doe (DOB: 01/15/1980) presented with..."

Example 2:
"Account #1234-5678-9012-3456 was credited..."
```

### Generation Method

[Brief description of how to create synthetic test data]

```python
# Code snippet or reference to data generation script
# See data_generator.py for full implementation
```

## Configuration Levels

### Level 1: Out-of-the-Box

**Description**: Default Presidio configuration using built-in recognizers and spaCy NLP engine.

**Configuration**:
```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(text=sample_text, language="en")
```

**Performance Results**:
- **Precision**: [0.XX]
- **Recall**: [0.XX]
- **F₂ Score**: [0.XX]
- **Latency**: [XX ms/sample]

**Strengths**:
- [What works well with this approach]

**Limitations**:
- [What this approach misses or struggles with]

### Level 2: Custom Recognizers

**Description**: Enhanced configuration with domain-specific recognizers, context words, or deny-lists.

**Configuration**:
```python
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer

# Define custom recognizer
custom_recognizer = PatternRecognizer(
    supported_entity="CUSTOM_ENTITY",
    patterns=[
        Pattern("pattern_name", r"regex_pattern", 0.85),
    ],
)

analyzer = AnalyzerEngine()
analyzer.registry.add_recognizer(custom_recognizer)
results = analyzer.analyze(text=sample_text, language="en")
```

**Performance Results**:
- **Precision**: [0.XX]
- **Recall**: [0.XX]
- **F₂ Score**: [0.XX]
- **Latency**: [XX ms/sample]

**Strengths**:
- [Improvements over Level 1]

**Limitations**:
- [Remaining challenges]

### Level 3: Custom Model (Optional)

**Description**: Fine-tuned transformer or custom NER model for domain-specific entity recognition.

**Configuration**:
```python
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

# Configure custom model
config = {
    "nlp_engine_name": "transformers",
    "models": [
        {
            "lang_code": "en",
            "model_name": {"transformers": "your-model-name"}
        }
    ]
}

provider = NlpEngineProvider(nlp_configuration=config)
nlp_engine = provider.create_engine()
analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
results = analyzer.analyze(text=sample_text, language="en")
```

**Performance Results**:
- **Precision**: [0.XX]
- **Recall**: [0.XX]
- **F₂ Score**: [0.XX]
- **Latency**: [XX ms/sample]

**Strengths**:
- [Benefits of custom model]

**Limitations**:
- [Trade-offs, especially computational cost]

### Level 4: Hybrid/Best-Effort (Optional)

**Description**: Ensemble approach combining multiple techniques or using LLM-based detection.

**Configuration**:
```python
# Outline of hybrid approach
# May combine regex, NER, transformers, and LLM verification
```

**Performance Results**:
- **Precision**: [0.XX]
- **Recall**: [0.XX]
- **F₂ Score**: [0.XX]
- **Latency**: [XX ms/sample]

**Strengths**:
- [Maximum accuracy benefits]

**Limitations**:
- [Cost and latency considerations]

## Results Summary

### Performance Comparison

| Configuration Level | Precision | Recall | F₂ Score | Latency (ms) | Cost Factor |
|---------------------|-----------|--------|----------|--------------|-------------|
| 1. Out-of-the-box   | [0.XX]    | [0.XX] | [0.XX]   | [XX]         | 1x          |
| 2. Custom Recognizers | [0.XX]  | [0.XX] | [0.XX]   | [XX]         | 1.2x        |
| 3. Custom Model     | [0.XX]    | [0.XX] | [0.XX]   | [XX]         | 3x          |
| 4. Hybrid           | [0.XX]    | [0.XX] | [0.XX]   | [XX]         | 10x         |

### Key Findings

1. **[Finding 1]**: [Insight about what works best for this domain]
2. **[Finding 2]**: [Trade-off observation]
3. **[Finding 3]**: [Edge case behavior]

## Recommendations

### When to Use Each Level

**Level 1: Out-of-the-Box**
- ✅ Use when: [Conditions where default config is sufficient]
- ❌ Avoid when: [Scenarios where it underperforms]

**Level 2: Custom Recognizers**
- ✅ Use when: [Best scenarios for custom recognizers]
- ❌ Avoid when: [When additional customization needed]

**Level 3: Custom Model**
- ✅ Use when: [Justification for custom model investment]
- ❌ Avoid when: [When simpler approaches suffice]

**Level 4: Hybrid**
- ✅ Use when: [Maximum accuracy scenarios]
- ❌ Avoid when: [Cost/latency prohibitive]

### Adapting to Your Use Case

[Guidance on how to adapt this recipe to variations of the scenario]

1. **If your data has [characteristic]**: Consider [adjustment]
2. **If you need [requirement]**: Try [approach]
3. **If you're limited by [constraint]**: Alternative is [solution]

## Implementation Guide

### Prerequisites

```bash
# Install required packages
pip install presidio-analyzer presidio-anonymizer
pip install [other dependencies]
python -m spacy download en_core_web_lg
```

### Quick Start

```python
# Minimal working example
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

# Your recommended configuration
analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# Example usage
text = "[sample text]"
results = analyzer.analyze(text=text, language="en")
anonymized = anonymizer.anonymize(text=text, analyzer_results=results)
print(anonymized.text)
```

### Full Notebook

For the complete implementation with detailed explanations, see the [Jupyter notebook](recipe.ipynb).

## Evaluation Methodology

### Dataset
- **Size**: [number] samples
- **Source**: [How data was obtained/generated]
- **Ground Truth**: [How labels were created]

### Metrics Calculation
```python
# Code showing how metrics were computed
from sklearn.metrics import precision_score, recall_score
# ...
```

### Test Environment
- **Hardware**: [CPU/GPU specs]
- **Software**: Python [version], Presidio [version]
- **Benchmark Date**: [YYYY-MM-DD]

## Known Limitations

1. **[Limitation 1]**: [Description and potential workaround]
2. **[Limitation 2]**: [Description and impact]
3. **[Limitation 3]**: [When this approach may not work]

## Future Improvements

- [Potential enhancement 1]
- [Potential enhancement 2]
- [Areas for further research]

## References

- [Relevant documentation links]
- [External resources or papers]
- [Related Presidio samples]

## Contributing

Found a better approach or identified issues with this recipe? Please [open an issue](https://github.com/microsoft/presidio/issues) or submit a pull request!

---

**Recipe Information**:
- **Author**: [Your Name/Organization]
- **Version**: 1.0
- **Last Updated**: [YYYY-MM-DD]
- **Presidio Version**: [X.X.X]
- **License**: MIT
