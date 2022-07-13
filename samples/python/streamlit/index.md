# Simple demo website for Presidio
Here's a simple app, written in pure Python, to create a demo website for Presidio.
The app is based on the [streamlit](https://streamlit.io/) package.

## Requirements
1. Install dependencies (preferably in a virtual environment)

```sh
pip install streamlit pandas presidio-analyzer presidio-anonymizer
```

2. Download the [presidio_streamlit.py](presidio_streamlit.py) file.
3. *Optional*: Update the `analyzer_engine` and `anonymizer_engine` functions for your specific implementation 
3. Start the app:

```sh
streamlit run presidio_streamlit.py
```

## Output
Output should be similar to this screenshot:
![image](https://user-images.githubusercontent.com/3776619/120109161-efe21080-c170-11eb-8a29-9eaf71e722ee.png)
