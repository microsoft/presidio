**Note:** Examples are made with [HTTPie](https://httpie.org/)

***Sample 1***

1. Analyze text
    ```sh
    echo -n '{"text":"John Smith lives in New York. We met yesterday morning in Seattle. I called him before on (212) 555-1234 to verify the appointment. He also told me that his drivers license is AC111921", "analyzeTemplate":{"allFields":true}  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
    ```

***Sample 2***

You can also create reusable templates

1. Create an analyzer project
    ```sh
    echo -n '{"allFields":true}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
    ```

2. Analyze text
    ```sh
    echo -n '{"text":"my credit card number is 2970-84746760-9907 345954225667833 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
    ```

***Sample 3***

1. Create an analyzer project
    ```sh
    echo -n '{"fields":[{"name":"PHONE_NUMBER"}, {"name":"LOCATION"}, {"name":"DATE_TIME"}]}' | http <api-service-address>/api/v1/templates/<my-project>/analyze/<my-template-name>
    ```

2. Analyze text
    ```sh
    echo -n '{"text":"We met yesterday morning in Seattle and his phone number is (212) 555 1234", "AnalyzeTemplateId":"<my-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/analyze
    ```

***Sample 4***

1. Create an anonymizer template (This template replaces values in PHONE_NUMBER and redacts CREDIT_CARD)
    ```sh
    echo -n '{"fieldTypeTransformations":[{"fields":[{"name":"PHONE_NUMBER"}],"transformation":{"replaceValue":{"newValue":"\u003cphone-number\u003e"}}},{"fields":[{"name":"CREDIT_CARD"}],"transformation":{"redactValue":{}}}]}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize/<my-anonymize-template-name>
    ```

2. Anonymize text
    ```sh
    echo -n '{"text":"my phone number is 057-555-2323 and my credit card is 4961-2765-5327-5913", "AnalyzeTemplateId":"<my-analyze-template-name>", "AnonymizeTemplateId":"<my-anonymize-template-name>"  }' | http <api-service-address>/api/v1/projects/<my-project>/anonymize
    ```

***Sample 5 (Image anonymization)***

1. Create an anonymizer image template (This template redact values with black color)
    ```sh
    echo -n '{"fieldTypeGraphics":[{"graphic":{"fillColorValue":{"blue":0,"red":0,"green":0}}}]}' | http <api-service-address>/api/v1/templates/<my-project>/anonymize-image/<my-anonymize-image-template-name>
    ```

2. Anonymize image
    ```sh
    http -f POST <api-service-address>/api/v1/projects/<my-project>/anonymize-image detectionType='OCR' analyzeTemplateId='<my-analyze-template-name>' anonymizeTemplateId='<my-anonymize-template-name>' imageType='image/png' file@~/test-ocr.png > test-output.png
    ```