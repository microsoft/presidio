# Integration with Semantic Kernel Sample

## Intro

This sample shows how presidio can be integrated with semantic kernel to make sure no PII is passed in the prompt and no PII is returned in the response.

For example having the prompt: 
```
Tell me about Madonna
```

Without the sample the answer would be:
```
Madonna is an American singer, songwriter, actress, and businesswoman. She was born on August 16, 1958, in Bay City, Michigan. Madonna is known for her provocative and controversial image, as well as her ability to constantly reinvent herself throughout her career.

She rose to fame in the 1980s with hits such as "Like a Virgin," "Material Girl," and "Papa Don't Preach." BIP has sold over 300 million records worldwide, making her the best-selling female recording artist of all time.

In addition to her music career, BIP has also acted in several films, including "Desperately Seeking BIP," "Evita," and "A League of Their Own." She has also been involved in various philanthropic efforts, including the founding of the Raising Malawi charity to support orphans and vulnerable children in Malawi.

Madonna has been recognized with numerous awards throughout her career, including seven Grammy Awards, two Golden Globe Awards
```

Using the sample we would get the answer:
```
I'm sorry, I cannot provide information about "SomeName" as it is too vague and could refer to anything or anyone. Can you please provide more context or details?
```

We can see in this case the prompt was anonymized and no information passed to the AI.
Same would be aplied on the response in case it did contain any peronal information.

## Prerequisites

- Semantic kernel python package - `python -m pip install semantic-kernel`
- [Presidio](docs/installation.md)

## Getting Started

To get started with the demo you will need to provide the credentials for the OpenAI instance. 
Make sure you have an [Open AI API Key](https://openai.com/api/) or [Azure Open AI service key](https://learn.microsoft.com/azure/cognitive-services/openai/quickstart?pivots=rest-api) and the deployment name.
Copy those keys into a .env file  based on the .env.sample

Running the demo: `python anonymize-conversation.py`
