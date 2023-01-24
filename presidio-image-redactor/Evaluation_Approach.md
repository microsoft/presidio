# Evaluating DICOM de-identification

## Table of Contents

* [Introduction](#introduction)
* [Ground truth format](#ground-truth-format)
* [Creating ground truth files](#creating-ground-truth-files)
* [Evaluating de-identification performance](#evaluating-de-identification-performance)

## Introduction

We can evaluate the performance of the `DicomImageRedactorEngine` DICOM de-identification by using the `DicomImagePiiVerifyEngine`. The evaluation results consist of:

* Image with bounding boxes identifying detected Personal Health Information (PHI)
* All positives (True Positives and False Positives)
* Precision
* Recall

## Ground truth format

Ground truth labels are stored as `.json` files containing filename as the highest level keys. Each filename object consists of an item for each individual entity.

```json
{
    "your/dicom/dir/file_0.dcm": [
        {
            "label": "DAVIDSON",
            "left": 25,
            "top": 25,
            "width": 241,
            "height": 37
        },
        {
            "label": "DOUGLAS",
            "left": 287,
            "top": 25,
            "width": 230,
            "height": 36
        },
        {
            "label": "[M]",
            "left": 535,
            "top": 25,
            "width": 60,
            "height": 45
        },
        {
            "label": "01.09.2012",
            "left": 613,
            "top": 26,
            "width": 226,
            "height": 35
        },
        {
            "label": "06.16.1976",
            "left": 170,
            "top": 72,
            "width": 218,
            "height": 35
        }
    ],
    "your/dicom/dir/file_1.dcm": [
        ...
    ]
}
```

*Return to the [Table of Contents](#table-of-contents)*

## Creating ground truth files

The `DicomImagePiiVerifyEngine` class can be used to assist in ground truth label generation. Use the following code snippet to generate the verification image, OCR results, and NER (analyzer) results.

```python
import pydicom
from presidio_image_redactor import DicomImagePiiVerifyEngine

# Initialize engine
dicom_engine = DicomImagePiiVerifyEngine()

# Choose your file to create ground truth for
filename = "path/to/your/file.dcm"
instance = pydicom.dcmread(filename)
padding_width = 25

# Get OCR and NER results
verification_image, ocr_results, analyzer_results = dicom_engine.verify_dicom_instance(instance, padding_width)

# Format results for more direct comparison
ocr_results_formatted = dicom_engine.bbox_processor.get_bboxes_from_ocr_results(ocr_results)
analyzer_results_formatted = dicom_engine.bbox_processor.get_bboxes_from_analyzer_results(analyzer_results)
```

By looking at the output of `verify_dicom_instance`, we can create a ground truth labels json.

Save `analyzer_results_formatted` as a json file and then perform the following

1. Group the results into a new item with the file name set as the key.
2. For each item in this group:
    a. Remove the "entity_type" field and value.
    b. Add a new "label" field with the value set to the ground truth text PHI with matching coordinate as you can see in the formatted OCR results and verification image.

Then check that your ground truth json contains all the text PHI you can visually confirm in the DICOM image. If something is not detected by the OCR or NER, you will need to manually add the item yourself.

Pixel position and size data can be obtained using any labeling software or imaging processing software (e.g., MS Paint) on the verification image.

> *Note: When manually specifying pixel position, make sure to account for any padding introduced in the OCR process (default padding added is 25 pixels).*

### Example

Let's say we ran the above code block and see the following for `ocr_results_formatted` and `analyzer_results_formatted`.

```json
// OCR Results (formatted)
[
    {
        "left": 25,
        "top": 25,
        "width": 241,
        "height": 37,
        "conf": 95.833916,
        "label": "DAVIDSON"
    },
    {
        "left": 287,
        "top": 25,
        "width": 230,
        "height": 36,
        "conf": 93.292221,
        "label": "DOUGLAS"
    }
]

// Analyzer Results (formatted)
[
    {
        "entity_type": "PERSON",
        "score": 1.0,
        "left": 25,
        "top": 25,
        "width": 241,
        "height": 37
    },
    {
        "entity_type": "PERSON",
        "score": 1.0,
        "left": 287,
        "top": 25,
        "width": 230,
        "height": 36
    }
]
```

Looking at the position and size values of the ground truth and detected text from the analyzer results, we can see that the first item in the analyzer results is likely "DAVIDSON" and the second is likely "DOUGLAS".

With this, we set our ground truth json to the following:

```json
// Ground truth json
{
    "path/to/your/file.dcm": [
        {
            "label": "DAVIDSON",
            "left": 25,
            "top": 25,
            "width": 241,
            "height": 37
        },
        {
            "label": "DOUGLAS",
            "left": 287,
            "top": 25,
            "width": 230,
            "height": 36
        }
    ]
}
```

*Return to the [Table of Contents](#table-of-contents)*

## Evaluating de-identification performance

The `DicomImagePiiVerifyEngine` can be used to evaluate DICOM de-identification performance.

```python
# Load ground truth for one file
with open(gt_path) as json_file:
    all_ground_truth = json.load(json_file)
ground_truth = all_ground_truth[file_of_interest]

# Select your DICOM instance
instance = pydicom.dcmread(file_of_interest)

# Evaluate the DICOM de-identification performance
_, eval_results = dicom_engine.eval_dicom_instance(instance, ground_truth)
```

You can also set optional arguments to see the effect of padding width, ground-truth matching tolerance, and OCR confidence threshold (e.g., `ocr_kwargs={"ocr_threshold": 50}`).

For a full demonstration, please see the [evaluation notebook](../docs/samples/python/example_dicom_redactor_evaluation.ipynb).

*Return to the [Table of Contents](#table-of-contents)*
