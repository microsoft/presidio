from dotenv import load_dotenv

load_dotenv()

import argparse
import os
import requests
from openai import AzureOpenAI
from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Input, Label, RichLog
from textual.containers import Horizontal, Vertical


def anonymize(text: str, language: str, session_id: str = None):
    url = os.getenv("API_URL").rstrip("/") + "/anonymize"

    body = {
        "text": text,
        "language": language,
    }
    if session_id is not None:
        body["session_id"] = session_id
    response = requests.post(url, json=body)
    response.raise_for_status()
    return response.json()


def deanonymize(text: str, session_id: str):
    url = os.getenv("API_URL").rstrip("/") + "/deanonymize"

    response = requests.post(
        url,
        json={
            "text": text,
            "session_id": session_id,
        },
    )
    response.raise_for_status()
    return response.json()


def get_llm_response(messages):
    client = AzureOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("OPENAI_ENDPOINT"),
    )
    deployment_name = os.getenv("OPENAI_DEPLOYMENT_NAME")
    response = client.chat.completions.create(
        model=deployment_name,
        messages=messages,
        max_tokens=100,
    )
    return response.choices[0].message.content


class InputApp(App):
    CSS = """
    Input {
        border: red 60%;
    }
    Input:focus {
        border: tall $success;
    }
    Label {
        margin: 1 2;
    }
    RichLog {
        margin-top: 1;
        margin-left: 1;
    }
    """

    def __init__(self, mode: str, language: str) -> None:
        super().__init__()
        self._mode = mode
        self._lang = language
        self._llm_message_history = [
            {
                "role": "system",
                "content": "You're a friendly assistant",
            },  # system prompt
        ]
        self._session_id = None

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="column"):
                yield Label("Human view")
                yield Input(
                    placeholder="Enter text...",
                    id="person_input",
                )
                yield RichLog(id="person_text", highlight=True, markup=True, wrap=True)

            with Vertical(classes="column"):
                yield Label("LLM view")
                yield Input(
                    placeholder="Enter text..." if self._mode == 'manual' else "use --mode manual to chat on behalf of the LLM",
                    id="llm_input",
                    disabled=True,
                )
                yield RichLog(id="llm_text", highlight=True, markup=True, wrap=True)

    @on(Input.Submitted)
    def handle(self, event: Input.Submitted) -> None:
        person_input = self.query_one("#person_input")
        llm_input = self.query_one("#llm_input")

        llm_text = self.query_one("#llm_text", RichLog)
        person_text = self.query_one("#person_text", RichLog)

        if event.input.id == "person_input":
            person_text.write("[bold magenta]  You:[/] " + event.value)

            anonymizer_response = anonymize(
                text=event.value, language=self._lang, session_id=self._session_id
            )
            text_for_llm = anonymizer_response["text"]
            self._session_id = anonymizer_response["session_id"]

            llm_text.write("[bold magenta]Input:[/] " + text_for_llm)
            self._llm_message_history.append({"role": "user", "content": text_for_llm})

            if self._mode == "llm":
                # let LLM generate response...
                llm_response = get_llm_response(self._llm_message_history)
                self._llm_message_history.append(
                    {"role": "assistant", "content": llm_response}
                )

                deanonymizer_response = deanonymize(
                    text=llm_response, session_id=self._session_id
                )
                text_for_person = deanonymizer_response["text"]

                person_text.write("[bold cyan]Agent:[/] " + text_for_person)
                llm_text.write("[bold cyan]  LLM:[/] " + llm_response)
            else:
                # ...or let the person enter the response manually
                llm_input.disabled = False
                person_input.disabled = True
                llm_input.focus()

        if event.input.id == "llm_input":
            deanonymizer_response = deanonymize(
                text=event.value, session_id=self._session_id
            )
            text_for_person = deanonymizer_response["text"]

            person_text.write("[bold cyan]Agent:[/] " + text_for_person)
            llm_text.write("[bold cyan]  LLM:[/] " + event.value)
            llm_input.disabled = True
            person_input.disabled = False
            person_input.focus()

        event.input.clear()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["manual", "llm"],
        default="llm",
        help="Chat mode: manual or llm",
    )
    parser.add_argument(
        "--language",
        default="en",
        help="Chat language: one of the languages supported by the API service",
    )
    args = parser.parse_args()

    app = InputApp(mode=args.mode, language=args.language)
    app.run()


if __name__ == "__main__":
    main()
