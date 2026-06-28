from collections import namedtuple
from typing import Optional

import openai
from openai import OpenAI, AzureOpenAI
import logging

logger = logging.getLogger("presidio-streamlit")

OpenAIParams = namedtuple(
    "open_ai_params",
    ["openai_key", "model", "api_base", "deployment_id", "api_version", "api_type"],
)


def call_completion_model(
    prompt: str,
    openai_params: OpenAIParams,
    max_tokens: Optional[int] = 256,
) -> str:
    """Creates a request for the OpenAI Completion service and returns the response.

    :param prompt: The prompt for the completion model
    :param openai_params: OpenAI parameters for the completion model
    :param max_tokens: The maximum number of tokens to generate.
    """
    if openai_params.api_type.lower() == "azure":
        client = AzureOpenAI(
            api_version=openai_params.api_version,
            api_key=openai_params.openai_key,
            azure_endpoint=openai_params.api_base,
            azure_deployment=openai_params.deployment_id,
        )
    else:
        client = OpenAI(api_key=openai_params.openai_key)

    response = client.completions.create(
        model=openai_params.model,
        prompt=prompt,
        max_tokens=max_tokens,
    )

    return response.choices[0].text.strip()


def create_prompt(anonymized_text: str) -> str:
    """
    Create the prompt with instructions to GPT-3.

    :param anonymized_text: Text with placeholders instead of PII values, e.g. My name is <PERSON>.
    """

    prompt = f"""
    Your role is to create synthetic text based on de-identified text with placeholders instead of Personally Identifiable Information (PII).
    Replace the placeholders (e.g. ,<PERSON>, {{DATE}}, {{ip_address}}) with fake values.

    Instructions:

    a. Use completely random numbers, so every digit is drawn between 0 and 9.
    b. Use realistic names that come from diverse genders, ethnicities and countries.
    c. If there are no placeholders, return the text as is.
    d. Keep the formatting as close to the original as possible.
    e. If PII exists in the input, replace it with fake values in the output.
    f. Remove whitespace before and after the generated text
    
    input: [[TEXT STARTS]] How do I change the limit on my credit card {{credit_card_number}}?[[TEXT ENDS]]
    output: How do I change the limit on my credit card 2539 3519 2345 1555?
    input: [[TEXT STARTS]]<PERSON> was the chief science officer at <ORGANIZATION>.[[TEXT ENDS]]
    output: Katherine Buckjov was the chief science officer at NASA.
    input: [[TEXT STARTS]]Cameroon lives in <LOCATION>.[[TEXT ENDS]]
    output: Vladimir lives in Moscow.
    
    input: [[TEXT STARTS]]{anonymized_text}[[TEXT ENDS]]
    output:"""
    return prompt
