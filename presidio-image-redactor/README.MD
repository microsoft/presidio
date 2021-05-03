# Presidio Image Redactor

***Please notice, this package is still in alpha and not production ready.***

## Description

The Presidio Image Redactor is a Python based module for detecting and redacting PII
text entities in images.

## Deploy Presidio image redactor to Azure

Use the following button to deploy presidio image redactor to your Azure subscription.

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Fmicrosoft%2Fpresidio%2Fmain%2Fpresidio-image-redactor%2Fdeploytoazure.json)

![Image Redactor Design](../docs/assets/image-redactor-design.png)

## Installation

Pre-requisites:

- Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) by following the
  instructions on how to install it for your operating system.

  For now, image redactor only supports version 4.0.0

### As package:

To get started with Presidio-image-redactor, run the following:

```sh
pip install presidio-image-redactor
```

Once Installed, run the following command to download the default spacy model needed for
Presidio Analyzer:

```sh
python -m spacy download en_core_web_lg
```

## Getting started

The engine will receive 2 parameters:

1. Image to redact.
2. Color fill to redact with, by default color fill will be black. Can either be an int
   or tuple (0,0,0)

```python
from PIL import Image
from presidio_image_redactor import ImageRedactorEngine

# Get the image to redact using PIL lib (pillow)
image = Image.open("presidio-image-redactor/tests/integration/resources/ocr_test.png")

# Initialize the engine
engine = ImageRedactorEngine()

# Redact the image with pink color
redacted_image = engine.redact(image, (255, 192, 203))

# save the redacted image 
redacted_image.save("new_image.png")
# uncomment to open the image for viewing
# redacted_image.show()
```

### As docker service:

In folder presidio/presidio-image-redactor run:

```
docker-compose up -d
```

### HTTP API

### redact

Receives an image and color fill (optional, default is black). Redact the image PII text
and returns a new redacted image.

```
POST /redact
```

Payload:

Sent as multipart-form. Contains image file and data of the required color fill.

```json
{
  "data": "{'color_fill':'0,0,0'}"
}
```

Result:

```
200 OK
```

curl example:

```
# use ocr_test.png as the image to redact, and 255 as the color fill. 
# out.png is the new redacted image received from the server.
curl -XPOST "http://localhost:3000/redact" -H "content-type: multipart/form-data" -F "image=@ocr_test.png" -F "data=\"{'color_fill':'255'}\"" > out.png
```

Python script example can be found under:
/presidio/e2e-tests/tests/test_image_redactor.py