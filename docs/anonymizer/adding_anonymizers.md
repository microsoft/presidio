# Supporting new types of PII anonymizers

Presidio anonymizer can be easily extended to support additional anonnymization methods.

## Extending the anonymizer for additional PII anonymizations:

1. Under the path presidio_anonymizr/anonymizers
2. Create a new file based on `Anonymizer`
3. Implement the methods: 
   - `anonymize` - gets the data and returns the new text expected to replace the old one.
   - `validate` - validate the parameters entered for the anonymizer exists and valid.
   - `anonymizer_name` - this method helps to automatically load the existing anonymizers.
4. Restart the anonymizer.

!!! note "Note"
    The list of anonymizers is being loaded dynamically each time Presidio Anonymizer is started.



