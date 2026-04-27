# Filtering recognizers by country

Many Presidio deployments only care about a subset of the world's PII —
e.g. a US-only healthcare app, or an EU-only data pipeline. Loading every
predefined country-specific recognizer in those scenarios means more
false positives, more memory, and more noise in the analyzer output.

`RecognizerRegistry.load_predefined_recognizers` accepts an optional
`countries` argument that narrows the country-specific recognizers to
the subset you care about, while always preserving locale-agnostic
recognizers (credit cards, emails, URLs, IBAN, dates, crypto, NER, NLP
engine recognizers, third-party integrations, …).

## Quick example

```python
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry

registry = RecognizerRegistry()
registry.load_predefined_recognizers(languages=["en"], countries=["us", "uk"])

analyzer = AnalyzerEngine(registry=registry)
```

The registry above contains all locale-agnostic recognizers (e.g. credit
card, email, URL) plus US- and UK-specific recognizers (US SSN, UK NHS,
UK NINO, …) — but excludes German, Spanish, Indian, Italian, Korean,
Polish, Singaporean, Swedish, Thai, Turkish, and other country
recognizers.

## How the filter works

Every recognizer carries a `country_code` attribute:

- `country_code is None` → **locale-agnostic**. Always loaded regardless
  of the country filter. This is the default for any recognizer that
  doesn't explicitly opt in.
- `country_code` set to an ISO 3166-1 alpha-2 string (e.g. `"us"`,
  `"uk"`, `"br"`) → **country-specific**. Only loaded when its code is
  in the `countries` argument.

The filter has a single rule:

| Recognizer's `country_code` | `countries=None` | `countries=["us"]` | `countries=["us", "uk"]` | `countries=[]` |
| --- | --- | --- | --- | --- |
| `None` (locale-agnostic) | ✅ kept | ✅ kept | ✅ kept | ✅ kept |
| `"us"` | ✅ kept | ✅ kept | ✅ kept | ❌ dropped |
| `"uk"` | ✅ kept | ❌ dropped | ✅ kept | ❌ dropped |
| `"de"` | ✅ kept | ❌ dropped | ❌ dropped | ❌ dropped |

Code comparison is **case-insensitive**: `"US"`, `"Us"`, `"us"` all work.

## Declaring `country_code` on your own recognizers

There are two equivalent ways to tag a custom recognizer:

### Option 1 — Class-level `COUNTRY_CODE` attribute

This is the path used by every predefined country-specific recognizer
in Presidio (`UsSsnRecognizer`, `UkNinoRecognizer`, `EsNifRecognizer`,
…) and is recommended for class-based recognizers:

```python
from presidio_analyzer import Pattern, PatternRecognizer


class BrCpfRecognizer(PatternRecognizer):
    """Recognize Brazilian CPF numbers."""

    COUNTRY_CODE = "br"

    PATTERNS = [
        Pattern("BR CPF (medium)", r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", 0.5),
    ]

    def __init__(self):
        super().__init__(
            supported_entity="BR_CPF",
            patterns=self.PATTERNS,
            supported_language="pt",
        )
```

The base `EntityRecognizer.__init__` reads the class attribute and
assigns it to `self.country_code`.

### Option 2 — Constructor argument

Useful for one-off recognizers, ad-hoc recognizers, and pattern
recognizers loaded from YAML:

```python
from presidio_analyzer import Pattern, PatternRecognizer

br_cpf = PatternRecognizer(
    supported_entity="BR_CPF",
    patterns=[Pattern("BR CPF", r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b", 0.5)],
    supported_language="pt",
    country_code="br",
)
```

If both are provided, the constructor argument wins over the class
attribute.

### Option 3 — YAML configuration

For YAML-defined custom recognizers, declare `country_code` next to the
other fields:

```yaml
recognizers:
  - name: "BR CPF Recognizer"
    supported_language: "pt"
    supported_entity: "BR_CPF"
    country_code: "br"
    patterns:
      - name: "br_cpf (medium)"
        regex: "\\b\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}\\b"
        score: 0.5
```

See the full example in
[`example_recognizers.yaml`](https://github.com/microsoft/presidio/blob/main/presidio-analyzer/presidio_analyzer/conf/example_recognizers.yaml).

## When to leave `country_code` unset

Some PII patterns are not anchored to a single country and should
remain locale-agnostic:

- Credit card numbers, email addresses, URLs, MAC addresses, crypto
  wallet addresses, dates, phone numbers (PhoneNumbers cover multiple
  countries via `phonenumbers`), …
- IBAN — geographically European-ish but not anchored to one country.
- Generic NER models (spaCy, Stanza, transformer-based recognizers).

Leave `country_code = None` (the default) for these. They will always
be loaded and the country filter will not touch them.

## Backwards compatibility

The filter is fully backwards compatible:

1. **Default behavior is unchanged.** Calling
   `load_predefined_recognizers()` without `countries` (or with
   `countries=None`) loads every predefined recognizer exactly as before.
2. **Untagged custom recognizers continue to work.** Any recognizer
   you've already deployed that does not declare `country_code` is
   treated as locale-agnostic and is never filtered out — regardless of
   the requested countries. The filter only excludes recognizers that
   have explicitly opted in via `country_code`.
3. **Predefined recognizers are pre-tagged.** Every recognizer under
   `presidio_analyzer.predefined_recognizers.country_specific.<country>`
   ships with its `COUNTRY_CODE` set to the appropriate ISO code, so
   `countries=["us"]` works on a fresh install with no further setup.

## Debugging

If you pass `countries=["br"]` and your custom Brazilian recognizer
disappears, the most likely cause is that the recognizer hasn't
declared `country_code="br"`. Two diagnostic helpers:

- `registry.get_country_codes()` returns the sorted list of country
  codes currently represented in the registry. If `"br"` is missing, no
  recognizer is tagged.
- The filter logs a `WARNING` whenever a requested country matches no
  recognizer in the input set, with a hint to set `country_code` on
  custom recognizers.

```python
import logging
logging.getLogger("presidio-analyzer").setLevel(logging.WARNING)

registry = RecognizerRegistry()
registry.load_predefined_recognizers(countries=["br"])
# WARNING ... Country filter: no recognizer matched country_code='br'.
#         If you have custom recognizers for 'br', set country_code='br'
#         on them to include them in country-filtered loads.
print(registry.get_country_codes())
# ['au', 'ca', 'de', 'es', 'fi', 'in', 'it', 'kr', 'ng', 'pl', 'se',
#  'sg', 'th', 'tr', 'uk', 'us']
```
