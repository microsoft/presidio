# Recipes Gallery

Welcome to the Presidio Recipes Gallery! This section provides curated, end-to-end examples demonstrating how to customize Microsoft Presidio for specific data privacy and de-identification scenarios.

## What are Recipes?

Recipes are comprehensive, reproducible examples tailored to common data domains and use cases. Each recipe goes beyond basic documentation to provide:

1. **Real-world Context**: Focused on specific scenarios like financial chatbot conversations, clinical notes, REST API logs, or multilingual content
2. **Synthetic Data Generation**: Methods for creating realistic test data that mimics your production environment
3. **Performance Benchmarks**: Evaluation metrics (precision, recall, F₂ score, and latency) across different Presidio configurations
4. **Progressive Complexity**: Examples ranging from out-of-the-box usage to advanced customization with transformers, LLMs, or hybrid approaches

## Why Use Recipes?

While Presidio's documentation covers the fundamentals, recipes bridge the gap between generic examples and production-ready implementations. They help you:

- **Evaluate Performance**: Understand Presidio's accuracy and speed for your specific domain before deployment
- **Customize Effectively**: Learn which recognizers, models, and configurations work best for different data types
- **Compare Approaches**: See side-by-side comparisons of different implementation strategies
- **Reduce Development Time**: Start with a working example close to your use case instead of building from scratch

## Recipe Structure

Each recipe follows a consistent structure:

- **Scenario Description**: The domain, data type, and privacy requirements
- **Data Generation**: Scripts or methods to create synthetic test data
- **Configuration Levels**: Multiple implementation approaches (e.g., out-of-the-box, custom recognizers, fine-tuned models)
- **Evaluation Results**: Performance metrics for each configuration
- **Jupyter Notebook**: Interactive, reproducible implementation with detailed explanations
- **Recommendations**: Guidance on when to use each approach based on accuracy/latency trade-offs

## Available Recipes

Currently, the recipes gallery is being built. Check back soon for recipes covering:

- **Financial Domain**: Chat conversations, transaction logs, customer service interactions
- **Healthcare Domain**: Clinical notes, patient records, medical reports
- **Retail/E-commerce**: Customer data, order information, support tickets
- **Enterprise**: REST API logs, database exports, internal communications
- **Multilingual**: Examples for Spanish, French, German, and other languages

## Recipe Performance Table (Coming Soon)

We're developing a comprehensive benchmark table that will show Presidio's performance across different domains and implementation levels. The table will include:

| Domain / Scenario | Out-of-the-box (spaCy) | Augmented (+ custom recognizers) | Custom Model (ML/Transformer) | Hybrid "Best-Effort" (ensemble/LLM) |
|-------------------|------------------------|----------------------------------|--------------------------------|-------------------------------------|
| **Financial (Chatbot)** | Coming Soon | Coming Soon | Coming Soon | Coming Soon |
| **Medical (Clinical Notes)** | Coming Soon | Coming Soon | Coming Soon | Coming Soon |
| **Retail (JSON REST)** | Coming Soon | Coming Soon | Coming Soon | Coming Soon |
| **Multilingual (Spanish)** | Coming Soon | Coming Soon | Coming Soon | Coming Soon |

Each cell will contain:
- **P** = Precision
- **R** = Recall  
- **F₂** = F₂ score (recall-weighted F-score)
- **Latency** = Average processing time per sample (milliseconds)
- **Notebook** = Link to interactive Jupyter notebook

## How to Use a Recipe

1. **Browse the recipes** to find one matching your domain or use case
2. **Review the notebook** to understand the approach and results
3. **Run the notebook** in your environment to reproduce the results
4. **Adapt the configuration** to your specific data and requirements
5. **Evaluate performance** on your own test dataset
6. **Deploy** the configuration that best meets your accuracy and performance needs

## Contributing a Recipe

We welcome community contributions! If you've developed a Presidio configuration for a specific domain and want to share it, please see our [contribution guidelines](CONTRIBUTING.md).

Good recipes to contribute:
- Focus on a specific, well-defined domain or scenario
- Include methods for generating or obtaining representative test data
- Provide evaluation metrics across multiple configuration levels
- Are well-documented with clear explanations
- Include a working Jupyter notebook

## Related Resources

- [Presidio Samples](../samples/index.md): Additional usage examples and integration patterns
- [Tutorial Series](../tutorial/index.md): Step-by-step guide to Presidio features
- [Best Practices for Developing Recognizers](../analyzer/developing_recognizers.md): Deep dive into creating custom PII recognizers
- [Presidio Research Repository](https://github.com/microsoft/presidio-research): Evaluation tools and research datasets
- [FAQ](../faq.md): Common questions about improving detection accuracy

## Questions or Feedback?

If you have questions about recipes or suggestions for new scenarios to cover, please:

- Open an issue on [GitHub](https://github.com/microsoft/presidio/issues)
- Email us at [presidio@microsoft.com](mailto:presidio@microsoft.com)
- Join the discussion in our [community channels](../community.md)

---

**Note**: The recipes gallery demonstrates Presidio's flexibility and customization capabilities. The goal is to show that Presidio is designed to be adapted to your specific needs, not used as a one-size-fits-all solution. Each recipe illustrates best practices for customization in different contexts.
