import openai

def set_openai_key(openai_key: str):
    """Set the OpenAI API key.
    :param openai_key: the open AI key (https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key)
    """
    openai.api_key = openai_key


def call_completion_model(
    prompt: str, model: str = "text-davinci-003", max_tokens: int = 512
) -> str:
    """Creates a request for the OpenAI Completion service and returns the response.

    :param prompt: The prompt for the completion model
    :param model: OpenAI model name
    :param max_tokens: Model's max_tokens parameter
    """

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
    Your role is to create synthetic text based on de-identified text with placeholders instead of personally identifiable information.
    Replace the placeholders (e.g. , , {{DATE}}, {{ip_address}}) with fake values.

    Instructions:

    Use completely random numbers, so every digit is drawn between 0 and 9.
    Use realistic names that come from diverse genders, ethnicities and countries.
    If there are no placeholders, return the text as is and provide an answer.
    input: How do I change the limit on my credit card {{credit_card_number}}?
    output: How do I change the limit on my credit card 2539 3519 2345 1555?
    input: {anonymized_text}
    output:
    """
    return prompt
