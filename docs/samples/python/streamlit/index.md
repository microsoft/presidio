# Simple demo website for Presidio
Here's a simple app, written in pure Python, to create a demo website for Presidio.
The app is based on the [streamlit](https://streamlit.io/) package.

## Requirements
1. Clone the repo / download the `streamlit` folder
2. Install dependencies (preferably in a virtual environment)

```sh
pip install -r requirements.txt
```

3. *Optional*: Update the `analyzer_engine` and `anonymizer_engine` functions for your specific implementation 
4. Start the app:

```sh
streamlit run presidio_streamlit.py
```

## Output
Output should be similar to this screenshot:
![image](https://user-images.githubusercontent.com/3776619/229591761-849d368e-49a8-4e71-890d-3407bca7a011.png)
