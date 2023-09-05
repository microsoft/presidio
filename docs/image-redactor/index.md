# Presidio Image Redactor

***Please notice, this package is still in beta and not production ready.***

## Description

The Presidio Image Redactor is a Python based module for detecting and redacting PII
text entities in images.
![img.png](../assets/image-redactor-design.png)

This module may also be used on medical DICOM images. The `DicomImageRedactorEngine` class may be used to redact text PII present as pixels in DICOM images.
![img.png](../assets/dicom-image-redactor-design.png)

!!! note "Note"
     This class only redacts pixel data and does not scrub text PHI which may exist in the DICOM metadata.
     We highly recommend using the DICOM image redactor engine to redact text from images BEFORE scrubbing metadata PHI.*

## Installation

Pre-requisites:

- Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract#installing-tesseract) by following the
  instructions on how to install it for your operating system.

!!! attention "Attention"
    For best performance, please use the most up-to-date version of Tesseract OCR. Presidio was tested with **v5.2.0**.

=== "Using pip"

    !!! note "Note"
        Consider installing the Presidio python packages on a virtual environment like venv or conda.
    
    To get started with Presidio-image-redactor,
    download the package and the `en_core_web_lg` spaCy model:
    
    ```sh
    pip install presidio-image-redactor
    python -m spacy download en_core_web_lg
    ```

=== "Using Docker"

    !!! note "Note"
        This requires Docker to be installed. [Download Docker](https://docs.docker.com/get-docker/).
    
    ```sh
    # Download image from Dockerhub
    docker pull mcr.microsoft.com/presidio-image-redactor
    
    # Run the container with the default port
    docker run -d -p 5003:3000 mcr.microsoft.com/presidio-image-redactor:latest
    ```

=== "From source"

    First, clone the Presidio repo. [See here for instructions](../installation.md#install-from-source).
    
    Then, build the presidio-image-redactor container:
    
    ```sh
    cd presidio-image-redactor
    docker build . -t presidio/presidio-image-redactor
    ```

## Getting started (standard image types)

=== "Python"

    Once the Presidio-image-redactor package is installed, run this simple script:
    
    ```python
    from PIL import Image
    from presidio_image_redactor import ImageRedactorEngine
    
    # Get the image to redact using PIL lib (pillow)
    image = Image.open("./docs/image-redactor/ocr_text.png")
    
    # Initialize the engine
    engine = ImageRedactorEngine()
    
    # Redact the image with pink color
    redacted_image = engine.redact(image, (255, 192, 203))
    
    # save the redacted image 
    redacted_image.save("new_image.png")
    # uncomment to open the image for viewing
    # redacted_image.show()
    
    ```

=== "As an HTTP server"

    You can run presidio image redactor as an http server using either python runtime or using a docker container.
    
    #### Using docker container
    
    ```sh
    cd presidio-image-redactor
    docker run -p 5003:3000 presidio-image-redactor 
    ```
    
    #### Using python runtime
    
    !!! note "Note"
        This requires the Presidio Github repository to be cloned.
    
    ```sh
    cd presidio-image-redactor
    python app.py
    # use ocr_test.png as the image to redact, and 255 as the color fill. 
    # out.png is the new redacted image received from the server.
    curl -XPOST "http://localhost:3000/redact" -H "content-type: multipart/form-data" -F "image=@ocr_test.png" -F "data=\"{'color_fill':'255'}\"" > out.png
    ```
Python script example can be found under:
/presidio/e2e-tests/tests/test_image_redactor.py

## Getting started (DICOM images)

=== "Python"

    Once the Presidio-image-redactor package is installed, run this simple script:
    
    ```python
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

    # Option 2: Redact from a loaded DICOM image and return redacted regions
    redacted_dicom_image, bboxes = engine.redact_and_return_bbox(dicom_image, fill="contrast")

    # Option 3: Redact from DICOM file and save redacted regions as json file
    engine.redact_from_file(input_path, output_dir, padding_width=25, fill="contrast", save_bboxes=True)

    # Option 4: Redact from directory and save redacted regions as json files
    ocr_kwargs = {"ocr_threshold": 50}
    engine.redact_from_directory("path/to/your/dicom", output_dir, fill="background", save_bboxes=True, ocr_kwargs=ocr_kwargs)
    ```

### Evaluating de-identification performance

If you are interested in evaluating the performance of the DICOM de-identification against ground truth labels, please see the [evaluating DICOM de-identification page](./evaluating_dicom_redaction.md).

### Side note for Windows

If you are using a Windows machine, you may run into issues if file paths are too long. Unfortunatley, this is not rare when working with DICOM images that are often nested in directories with descriptive names.

To avoid errors where the code may not recognize a path as existing due to the length of the characters in the file path, please [enable long paths on your system](https://learn.microsoft.com/en-us/answers/questions/293227/longpathsenabled.html).

### DICOM Data Citation

The DICOM data used for unit and integration testing for `DicomImageRedactorEngine` are stored in this repository with permission from the original dataset owners. Please see the dataset information as follows:

> Rutherford, M., Mun, S.K., Levine, B., Bennett, W.C., Smith, K., Farmer, P., Jarosz, J., Wagner, U., Farahani, K., Prior, F. (2021). A DICOM dataset for evaluation of medical image de-identification (Pseudo-PHI-DICOM-Data) [Data set]. The Cancer Imaging Archive. DOI: <https://doi.org/10.7937/s17z-r072>

## API reference

the [API Spec](https://microsoft.github.io/presidio/api-docs/api-docs.html#tag/Image-redactor)
for the Image Redactor REST API reference details
and [Image Redactor Python API](../api/image_redactor_python.md) for Python API reference
