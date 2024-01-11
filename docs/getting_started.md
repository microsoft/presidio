# Getting started with Presidio

## Simple flow

Using Presidio's modules as Python packages to get started:

===+ "Anonymize PII in text (Default spaCy model)"


    1. Install Presidio
        
        ```sh
        pip install presidio-analyzer
        pip install presidio-anonymizer
        python -m spacy download en_core_web_lg
        ```
    
    2. Analyze + Anonymize
    
        ```py
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        
        text="My phone number is 212-555-5555"
        
        # Set up the engine, loads the NLP module (spaCy model by default) 
        # and other PII recognizers
        analyzer = AnalyzerEngine()
        
        # Call analyzer to get results
        results = analyzer.analyze(text=text,
                                   entities=["PHONE_NUMBER"],
                                   language='en')
        print(results)
        
        # Analyzer results are passed to the AnonymizerEngine for anonymization
        
        anonymizer = AnonymizerEngine()
        
        anonymized_text = anonymizer.anonymize(text=text,analyzer_results=results)
        
        print(anonymized_text)
        ```

=== "Anonymize PII in text (transformers)"

    1. Install Presidio
        
        ```sh
        pip install "presidio-analyzer[transformers]"
        pip install presidio-anonymizer
        python -m spacy download en_core_web_sm
        ```
    
    2. Analyze + Anonymize
    
        ```py
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import TransformersNlpEngine
        from presidio_anonymizer import AnonymizerEngine
        
        text = "My name is Don and my phone number is 212-555-5555"
        
        # Define which transformers model to use
        model_config = [{"lang_code": "en", "model_name": {
            "spacy": "en_core_web_sm",  # use a small spaCy model for lemmas, tokens etc.
            "transformers": "dslim/bert-base-NER"
            }
        }]

        nlp_engine = TransformersNlpEngine(models=model_config)

        # Set up the engine, loads the NLP module (spaCy model by default) 
        # and other PII recognizers
        analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        
        # Call analyzer to get results
        results = analyzer.analyze(text=text, language='en')
        print(results)
        
        # Analyzer results are passed to the AnonymizerEngine for anonymization
        
        anonymizer = AnonymizerEngine()
        
        anonymized_text = anonymizer.anonymize(text=text, analyzer_results=results)
        
        print(anonymized_text)
        
        ```
        !!! tip "Tip: Downloading models"
            If not available, the transformers model and the spacy model would be downloaded on the first call to the `AnalyzerEngine`. To pre-download, see [this doc](./analyzer/nlp_engines/transformers.md#downloading-a-pre-trained-model).

## Simple flow: Images

=== "Anonymize PII in images"

    1. Install presidio-image-redactor
    
        ```sh
        pip install presidio-image-redactor
        ```
       
    2. Redact PII from image
    
        ```py
        from presidio_image_redactor import ImageRedactorEngine
        from PIL import Image
        
        image = Image.open(path_to_image_file)
        
        redactor = ImageRedactorEngine()
        redactor.redact(image=image)
        ```

=== "Redact text PII in DICOM images"

    1. Install presidio-image-redactor
    
        ```sh
        pip install presidio-image-redactor
        ```
       
    2. Redact text PII from DICOM image
    
        ```py
        import pydicom
        from presidio_image_redactor import DicomImageRedactorEngine

        # Set input and output paths
        input_path = "path/to/your/dicom/file.dcm"
        output_dir = "./output"

        # Initialize the engine
        engine = DicomImageRedactorEngine()

        # Option 1: Redact from a loaded DICOM image
        dicom_image = pydicom.dcmread(input_path)
        redacted_dicom_image = engine.redact(dicom_image, fill="contrast")

        # Option 2: Redact from DICOM file
        engine.redact_from_file(input_path, output_dir, padding_width=25, fill="contrast")

        # Option 3: Redact from directory
        engine.redact_from_directory("path/to/your/dicom", output_dir, padding_width=25, fill="contrast")
        ```
---

## Read more

- [Installing Presidio](installation.md)
- [PII detection in text](analyzer/index.md)
- [PII anonymization in text](anonymizer/index.md)
- [PII redaction in images](image-redactor/index.md)
- [Discussion board](https://github.com/microsoft/presidio/discussions)
