# Supporting new types of PII operators

Operators are the presidio-anonymizer actions over the text.

There are two types of operators:
- Anonymize (hash, replace, redact, encrypt, mask)
- Deanonymize (decrypt)

Presidio anonymizer can be easily extended to support additional anonymization and deanonymization methods.

## Extending presidio-anonymizer for additional PII operators:

1. Under the path presidio_anonymizer/operators create new python class implementing the abstract [Operator](https://github.com/microsoft/presidio/blob/main/presidio-anonymizer/presidio_anonymizer/operators/operator.py) class
2. Implement the methods:
    - `operate` - gets the data and returns a new text expected to replace the old one.
    - `validate` - validate the parameters entered for the anonymizer exists and valid.
    - `operator_name` - this method helps to automatically load the existing anonymizers.
    - `operator_type` - either Anonymize or Deanonymize. Will be mapped to the proper engine.
3. Add the class to presidio_anonymizer/operators/__init__.py.
4. Restart the anonymizer.

!!! note "Note"
    The list of operators is being loaded dynamically each time Presidio Anonymizer is started.
