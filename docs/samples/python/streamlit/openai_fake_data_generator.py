import logging
from collections import namedtuple
from typing import Optional

from openai import AzureOpenAI, OpenAI

logger = logging.getLogger("presidio-streamlit")

OpenAIParams = namedtuple(
    "open_ai_params",
    ["openai_key", "model", "api_base", "deployment_id", "api_version", "api_type"],
)


def call_completion_model(
    prompt: str,
    openai_params: OpenAIParams,
    max_tokens: Optional[int] = 512,
) -> str:
    """Create a request to the OpenAI Chat Completions API and return the response.

    :param prompt: The prompt for the chat model
    :param openai_params: OpenAI parameters for the chat model
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

    response = client.chat.completions.create(
        model=openai_params.model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=1.0,
    )

    return _strip_scaffolding(response.choices[0].message.content)


def _strip_scaffolding(text: str) -> str:
    """Remove few-shot scaffolding the model may echo back into its answer."""
    text = text.strip()
    for marker in ("[[TEXT STARTS]]", "[[TEXT ENDS]]"):
        text = text.replace(marker, "")
    text = text.strip()
    for prefix in ("output:", "input:"):
        if text.lower().startswith(prefix):
            text = text[len(prefix) :].strip()
    return text


def create_prompt(anonymized_text: str) -> str:
    """
    Create the prompt instructing the model to synthesize fake PII values.

    :param anonymized_text: Text with placeholders instead of PII values,
        e.g. "My name is <PERSON>." (Presidio's ``replace`` operator output).
    """

    prompt = f"""Your task is to create synthetic text from de-identified text that contains placeholders (such as <PERSON>, <DATE_TIME>, <IP_ADDRESS>, <CREDIT_CARD>, <US_SSN>) instead of Personally Identifiable Information (PII). Replace every placeholder with a realistic, fake value of the matching type, and leave all other text unchanged.

Instructions:
1. Replace each placeholder with a believable fake value; keep the original wording, punctuation and formatting otherwise.
2. Use realistic names spanning diverse genders, ethnicities and countries.
3. NUMBERS MUST BE RANDOM: for every numeric value (SSN, credit card, phone, passport, bank account, IBAN, etc.), pick each digit independently at random (0-9). Never use sequential digits (e.g. 123-45-6789), repeated digits (e.g. 1111 1111), counting patterns (e.g. 123456789012), or placeholder-looking values like X123456789. The digits should look like real, messy, random data.
4. Keep each fake value plausibly valid in length/format for its type (e.g. a US SSN is ddd-dd-dddd, a credit card is 16 digits in groups of 4).
5. If there are no placeholders, return the input text unchanged.
6. Return ONLY the resulting text — no explanations, no quotes, and do NOT include the markers "[[TEXT STARTS]]", "[[TEXT ENDS]]", "input:" or "output:" anywhere in your answer.

input: [[TEXT STARTS]]How do I change the limit on my credit card <CREDIT_CARD>?[[TEXT ENDS]]
output: How do I change the limit on my credit card 4716 9028 3517 6240?
input: [[TEXT STARTS]]<PERSON> was the chief science officer at <ORGANIZATION>.[[TEXT ENDS]]
output: Katherine Buckjov was the chief science officer at NASA.
input: [[TEXT STARTS]]<PERSON>'s SSN is <US_SSN> and her phone is <PHONE_NUMBER>.[[TEXT ENDS]]
output: Mateo Okafor's SSN is 627-48-1903 and his phone is (415) 802-7356.

input: [[TEXT STARTS]]{anonymized_text}[[TEXT ENDS]]
output:"""
    return prompt
