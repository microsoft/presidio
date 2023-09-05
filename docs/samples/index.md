# Samples

| Topic       | Type                                  | Sample                                                                                                                                          |
| :---------- |:--------------------------------------| :---------------------------------------------------------------------------------------------------------------------------------------------- |
| Usage       | Python Notebook                       | [Presidio Basic Usage Notebook](python/presidio_notebook.ipynb)  |
| Usage       | Python Notebook                       | [Customizing Presidio Analyzer](python/customizing_presidio_analyzer.ipynb) |
| Usage       | Python Notebook                       | [Analyzing structured / semi-structured data in batch](python/batch_processing.ipynb)|
| Usage       | Python Notebook                       | [Encrypting and Decrypting identified entities](python/encrypt_decrypt.ipynb)|
| Usage       | Python Notebook                       | [Getting the identified entity value using a custom Operator](python/getting_entity_values.ipynb)|
| Usage       | Python Notebook                       | [Anonymizing known values](https://github.com/microsoft/presidio/blob/main/docs/samples/python/Anonymizing%20known%20values.ipynb)
| Usage       | Python Notebook                       | [Redacting text PII from DICOM images](https://github.com/microsoft/presidio/blob/main/docs/samples/python/example_dicom_image_redactor.ipynb)
| Usage       | Python Notebook                       | [Using an allow list with image redaction](https://github.com/microsoft/presidio/blob/main/docs/samples/python/image_redaction_allow_list_approach.ipynb)
| Usage       | Python Notebook                       | [Annotating PII in a PDF](https://github.com/microsoft/presidio/blob/main/docs/samples/python/example_pdf_annotation.ipynb)
| Usage       | Python Notebook                       | [Integrating with external services](https://github.com/microsoft/presidio/blob/main/docs/samples/python/integrating_with_external_services.ipynb) |
| Usage       | Python                                | [Remote Recognizer](https://github.com/microsoft/presidio/blob/main/docs/samples/python/example_remote_recognizer.py) |
| Usage       | Python                                | [Text Analytics as a Remote Recognizer](https://github.com/microsoft/presidio/blob/main/docs/samples/python/text_analytics/index.md)  |
| Usage       | Python                                | [Analyze and Anonymize CSV file](https://github.com/microsoft/presidio/blob/main/docs/samples/python/process_csv_file.py) |
| Usage       | Python                                | [Using Flair as an external PII model](https://github.com/microsoft/presidio/blob/main/docs/samples/python/flair_recognizer.py)|
| Usage       | Python                                | [Using Transformers as an external PII model](python/transformers_recognizer/index.md)|
| Usage       | Python                                | [Passing a lambda as a Presidio anonymizer using Faker](https://github.com/microsoft/presidio/blob/main/docs/samples/python/example_custom_lambda_anonymizer.py)|
| Usage       | REST API (postman)                    | [Presidio as a REST endpoint](docker/index.md)|
| Deployment  | App Service                           | [Presidio with App Service](deployments/app-service/index.md)|
| Deployment  | Kubernetes                            | [Presidio with Kubernetes](deployments/k8s/index.md)|
| Deployment  | Spark/Azure Databricks                | [Presidio with Spark](deployments/spark/index.md)|
| Deployment  | Azure Data Factory with App Service   | [ETL for small dataset](deployments/data-factory/presidio-data-factory.md#option-1-presidio-as-an-http-rest-endpoint) |
| Deployment  | Azure Data Factory with Databricks    | [ETL for large datasets](deployments/data-factory/presidio-data-factory.md#option-2-presidio-on-azure-databricks) |
| ADF Pipeline  | Azure Data Factory | [Add Presidio as an HTTP service to your Azure Data Factory](deployments/data-factory/presidio-data-factory-template-gallery-http.md) |
| ADF Pipeline  | Azure Data Factory | [Add Presidio on Databricks to your Azure Data Factory](deployments/data-factory/presidio-data-factory-template-gallery-databricks.md) |
| Demo | Streamlit | [Create a simple demo app using Streamlit](python/streamlit/index.md)
