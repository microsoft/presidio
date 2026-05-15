supported\_languages:

&#x20; - en

&#x20; - de



\# Building Custom Presidio Docker Images



\## Overview



This guide explains how to build custom Presidio Docker images with support for additional languages beyond English.



\*Common Use Cases:\*

\- Add German, Spanish, French language support

\- Use different NLP backends (Spacy vs Stanza)

\- Optimize for production deployments



\---



\## Key Files to Modify



When customizing Presidio, you'll work with configuration files in:

presidio-analyzer/presidio\_analyzer/conf

\### Important Configuration Files



1\. \*default\_recognizers.yaml\*

&#x20;  - Defines which PII recognizers are enabled/disabled

&#x20;  - Specifies language support for each recognizer

&#x20;  - Location: presidio-analyzer/presidio\_analyzer/conf/default\_recognizers.yaml



2\. \*spacy.yaml / stanza.yaml\*

&#x20;  - Configure which NLP backend to use

&#x20;  - Location: presidio-analyzer/presidio\_analyzer/conf/



\### Example: Add German Language Support



1\. Open presidio-analyzer/presidio\_analyzer/conf/default\_recognizers.yaml



2\. Find the "Germany recognizers" section (around line 312)



3\. Change enabled: false to enabled: true:



```yaml

\- name: DeTaxIdRecognizer

&#x20; supported\_languages:

&#x20; - de

&#x20; type: predefined

&#x20; enabled: true



\- name: DePassportRecognizer

&#x20; supported\_languages:

&#x20; - de

&#x20; type: predefined

&#x20; enabled: true

