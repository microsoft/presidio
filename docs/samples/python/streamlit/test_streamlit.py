from presidio_helpers import analyzer_engine, analyze, anonymize


def test_streamlit_logic():
    st_model = "en"  # st_model = "StanfordAIMI/stanford-deidentifier-base"
    st_model_package = "stanza"  ##st_model_package = "HuggingFace"
    st_ta_key = None
    st_ta_endpoint = None

    analyzer_params = (st_model_package, st_model, st_ta_key, st_ta_endpoint)

    # Read default text
    with open("demo_text.txt") as f:
        demo_text = f.readlines()

    st_text = "".join(demo_text)

    # instantiate and cache AnalyzerEngine
    analyzer_engine(*analyzer_params)

    # Analyze
    st_analyze_results = analyze(
        *analyzer_params,
        text=st_text,
        entities="All",
        language="en",
        score_threshold=0.35,
        return_decision_process=True,
        allow_list=[],
        deny_list=[],
    )

    # Anonymize
    st_anonymize_results = anonymize(
        text=st_text,
        operator="replace",
        mask_char=None,
        number_of_chars=None,
        encrypt_key=None,
        analyze_results=st_analyze_results,
    )

    assert st_anonymize_results.text != ""
