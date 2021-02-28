# Supporting new types of PII anonymizers

Presidio anonymizer can be easily extended to support additional anonnymization methods.

## Extending the anonymizer for additional PII anonymizations:

1. Under the path presidio_anonymizer/anonymizers create  new python class implemeting the abstract [Anonymizer](https://github.com/microsoft/presidio/blob/main/presidio-anonymizer/presidio_anonymizer/anonymizers/anonymizer.py) class 
2. Implement the methods: 
    - `anonymize` - gets the data and returns a new text expected to replace the old one.
    - `validate` - validate the parameters entered for the anonymizer exists and valid.
    - `anonymizer_name` - this method helps to automatically load the existing anonymizers.
3. Add the class to presidio_anonymizer/anonymizers/__init__.py.    
4. Restart the anonymizer.

!!! note "Note"
    The list of anonymizers is being loaded dynamically each time Presidio Anonymizer is started.

