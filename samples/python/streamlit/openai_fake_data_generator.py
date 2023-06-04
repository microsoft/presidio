from collections import namedtuple
from typing import Optional

import openai
import logging

logger = logging.getLogger("presidio-streamlit")

OpenAIParams = namedtuple(
    "open_ai_params",
    ["openai_key", "model", "api_base", "deployment_name", "api_version", "api_type"],
)


def set_openai_params(openai_params: OpenAIParams):
    """Set the OpenAI API key.
    :param openai_params: OpenAIParams object with the following fields: key, model, api version, deployment_name,
    The latter only relate to Azure OpenAI deployments.
    """
    openai.api_key = openai_params.openai_key
    openai.api_version = openai_params.api_version
    if openai_params.api_base:
        openai.api_base = openai_params.api_base
        openai.api_type = openai_params.api_type


def call_completion_model(
    prompt: str,
    model: str = "text-davinci-003",
    max_tokens: int = 512,
    deployment_id: Optional[str] = None,
) -> str:
    """Creates a request for the OpenAI Completion service and returns the response.

    :param prompt: The prompt for the completion model
    :param model: OpenAI model name
    :param max_tokens: Model's max_tokens parameter
    :param deployment_id: Azure OpenAI deployment ID
    """
    if deployment_id:
        response = openai.Completion.create(
            deployment_id=deployment_id, model=model, prompt=prompt, max_tokens=max_tokens
        )
    else:
        response = openai.Completion.create(
            model=model, prompt=prompt, max_tokens=max_tokens
        )

    return response["choices"][0].text


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
    c. If there are no placeholders, return the text as is and provide an answer.
    d. Keep the formatting as close to the original as possible.
    e. If PII exists in the input, replace it with fake values in the output.
    
    input: How do I change the limit on my credit card {{credit_card_number}}?
    output: How do I change the limit on my credit card 2539 3519 2345 1555?
    input: <PERSON> was the chief science officer at <ORGANIZATION>.
    output: Katherine Buckjov was the chief science officer at NASA.
    input: Cameroon lives in <LOCATION>.
    output: Vladimir lives in Moscow.
    input: {anonymized_text}
    output:
    """
    return prompt
