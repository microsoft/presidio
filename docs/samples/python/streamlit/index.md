# Simple demo website for Presidio
Here's a simple app, written in pure Python, to create a demo website for Presidio.
The app is based on the [streamlit](https://streamlit.io/) package.

A live version can be found here: https://huggingface.co/spaces/presidio/presidio_demo

## Requirements
1. Clone the repo and move to the `docs/samples/python/streamlit` folder
2. Install dependencies with [uv](https://docs.astral.sh/uv/) (creates an isolated virtual environment from `pyproject.toml`/`uv.lock`):

```sh
uv sync
```
> Note: This also installs additional packages such as `transformers`, `gliner` and `flair`
> (and the `en_core_web_lg` / `en_core_web_sm` spaCy models) which are not mandatory for using Presidio.

3. *Optional*: Update the analyzer configuration. The NER setups are defined declaratively as
   YAML files under `config/` and loaded via `AnalyzerEngineProvider` (see `presidio_analyzer_config.py`).
4. Start the app:

```sh
uv run streamlit run presidio_streamlit.py
```

5. Consider adding an `.env` file with the following environment variables, for further customizability:
```sh
OPENAI_TYPE="openai" #or "Azure"
OPENAI_KEY=YOUR_OPENAI_KEY
OPENAI_API_VERSION="2023-05-15"
```
## Output
Output should be similar to this screenshot:
![image](https://github.com/data-privacy-stack/presidio/assets/3776619/7d0eadf1-e750-4747-8b59-8203aa43cac8)
