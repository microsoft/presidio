import semantic_kernel as sk
from presidio_analyzer import AnalyzerEngine
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, OpenAIChatCompletion
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import RecognizerResult, OperatorConfig

# Semantic Kernel Setup

# Load settings from .env file
deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
# Create a semantic kernel
kernel = sk.Kernel()
# Configure AI service used by the kernel
kernel.add_chat_service( "chat_completion", AzureChatCompletion(deployment, endpoint, api_key))

# Presidio Setup
# Set up the engines
analyzer = AnalyzerEngine()
engine = AnonymizerEngine()

# Anonymize the prompt:
sk_prompt = "Tell me a story about John Smith."

prompt_analyzer_results = analyzer.analyze(text=sk_prompt,
                           entities=["PERSON"],
                           language='en')

anonymized_prompt = engine.anonymize(
    text= sk_prompt,
    analyzer_results=prompt_analyzer_results,
    operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
)


anonymized_function = kernel.create_semantic_function(anonymized_prompt.text, max_tokens=200, temperature=0, top_p=0.5)
summary = anonymized_function()


# Anonymize the AI output:

results = analyzer.analyze(text=summary.result,
                           entities=["PERSON"],
                           language='en')
result = engine.anonymize(
    text= summary.result,
    analyzer_results=results,
    operators={"PERSON": OperatorConfig("replace", {"new_value": "BIP"})},
)

print(f"Output: {result.text}") # Outputs a story about anonymic person