# Supporting new types of PII anonymization operators

Presidio anonymizer can be easily extended to support additional anonnymization operators.

## Extending the anonymizer for additional PII anonymization operators:

1. Under the path presidio_anonymizer/operators create new python class implementing the abstract [Operator](https://github.com/microsoft/presidio/blob/main/presidio-anonymizer/presidio_anonymizer/operators/operator.py) class 
2. Implement the methods: 
    - `operate` - gets the data and returns a new text expected to replace the old one.
    - `validate` - validate the parameters entered for the operator exists and valid.
    - `operator_name` - this method helps to automatically load the existing operator.
    - `operator_type` - for now, only the 'Anonymize' operators can be extended.
3. Add the class to presidio_anonymizer/operators/__init__.py.    
4. Restart the anonymizer.

!!! note "Note"
    The list of anonymization operators is being loaded dynamically each time Presidio Anonymizer is started.

