# Presidio Claude Code Plugin and Skills

This directory contains Claude Code plugins and skills for working with Microsoft Presidio, a comprehensive Data Protection and De-identification SDK.

## Overview

The Presidio toolkit provides Claude with comprehensive capabilities for:
- Detecting PII (Personally Identifiable Information) in text, images, and structured data
- Anonymizing sensitive data using various operators (redact, mask, hash, encrypt, replace)
- Creating custom PII recognizers for domain-specific patterns
- Processing images and DICOM medical files
- Handling structured data (DataFrames, CSV, JSON, Parquet)

## Directory Structure

```
.claude/
├── README.md                          # This file
├── plugins/
│   └── presidio-toolkit.json         # Plugin definition
└── skills/
    └── presidio-pii-detection/
        ├── SKILL.md                  # Main skill instructions
        ├── references/
        │   └── api_quick_reference.md # API documentation
        └── scripts/
            ├── analyze_text.py       # PII detection script
            └── anonymize_text.py     # Anonymization script
```

## Installation

### Prerequisites

```bash
# Install Presidio components
pip install presidio-analyzer presidio-anonymizer
python -m spacy download en_core_web_lg

# Optional: Image redaction
pip install presidio-image-redactor

# Optional: Structured data
pip install presidio-structured
```

### Installing the Plugin in Claude Code

The plugin is automatically available when you're working in this repository. Claude Code will detect the `.claude` directory and load the plugin.

To manually reference the skill, you can mention "presidio" or "PII" in your prompts, and Claude will automatically use the presidio-pii-detection skill.

## Skills

### presidio-pii-detection

**Description**: Comprehensive skill for detecting, analyzing, and anonymizing PII in text, images, and structured data.

**Capabilities**:
- Text PII detection and anonymization
- Custom recognizer creation
- Image and DICOM redaction
- Structured data anonymization
- Multi-language support
- Context-aware detection
- Reversible anonymization (encryption)

**When to Use**:
- User mentions PII, sensitive data, or privacy
- User asks about redacting or anonymizing data
- User needs to detect credit cards, SSNs, emails, phone numbers, etc.
- User works with documents containing personal information
- User needs GDPR, HIPAA, or privacy compliance

**Example Usage**:
```
# Claude will automatically use this skill when you ask:
"Help me detect and anonymize PII in this text: My SSN is 123-45-6789"
"I need to redact sensitive information from this document"
"How can I create a custom recognizer for employee IDs?"
```

## Scripts

### analyze_text.py

Detect PII entities in text.

```bash
# Analyze text
python .claude/skills/presidio-pii-detection/scripts/analyze_text.py "My phone is 555-1234"

# Analyze from file
python .claude/skills/presidio-pii-detection/scripts/analyze_text.py --file input.txt

# Detect specific entities
python .claude/skills/presidio-pii-detection/scripts/analyze_text.py \
    --entities PHONE_NUMBER EMAIL_ADDRESS \
    "Contact me at john@example.com or 555-1234"

# Save results to file
python .claude/skills/presidio-pii-detection/scripts/analyze_text.py \
    --file input.txt --output results.json
```

### anonymize_text.py

Anonymize PII in text.

```bash
# Anonymize text (default: replace)
python .claude/skills/presidio-pii-detection/scripts/anonymize_text.py \
    "My SSN is 123-45-6789"

# Redact PII
python .claude/skills/presidio-pii-detection/scripts/anonymize_text.py \
    --operator redact \
    "John's email is john@example.com"

# Mask PII
python .claude/skills/presidio-pii-detection/scripts/anonymize_text.py \
    --operator mask \
    "My credit card is 4111-1111-1111-1111"

# Hash PII
python .claude/skills/presidio-pii-detection/scripts/anonymize_text.py \
    --operator hash \
    "Patient SSN: 123-45-6789"

# Process file
python .claude/skills/presidio-pii-detection/scripts/anonymize_text.py \
    --file input.txt --output anonymized.txt --operator redact
```

## Using the Skill in Claude Code

The skill is automatically activated when you discuss topics related to:
- PII detection or anonymization
- Sensitive data or privacy
- Data protection or de-identification
- GDPR, HIPAA compliance
- Redacting or masking data
- Credit cards, SSNs, emails, phone numbers, etc.

### Example Interactions

**Basic Text Anonymization**:
```
User: "I have a document with customer data. How can I anonymize phone numbers and emails?"

Claude (using presidio-pii-detection skill):
"I'll help you anonymize phone numbers and emails using Presidio. Here's how..."
[Provides code example using AnalyzerEngine and AnonymizerEngine]
```

**Custom Recognizer**:
```
User: "I need to detect custom employee IDs in the format EMP-123456"

Claude (using presidio-pii-detection skill):
"I'll show you how to create a custom pattern recognizer for your employee ID format..."
[Provides PatternRecognizer example]
```

**Image Redaction**:
```
User: "Can you help me redact PII from a scanned document?"

Claude (using presidio-pii-detection skill):
"Yes, I can help you use Presidio's image redactor..."
[Provides ImageRedactorEngine example]
```

## Plugin Configuration

The plugin is defined in `plugins/presidio-toolkit.json`:

```json
{
  "name": "presidio-toolkit",
  "version": "1.0.0",
  "description": "Comprehensive toolkit for PII detection and anonymization",
  "skills": [
    "../skills/presidio-pii-detection"
  ]
}
```

## References

- **Main Repository Guide**: See `../claude.md` for comprehensive repository documentation
- **API Quick Reference**: See `skills/presidio-pii-detection/references/api_quick_reference.md`
- **Presidio Documentation**: https://microsoft.github.io/presidio
- **Presidio Repository**: https://github.com/microsoft/presidio

## Supported PII Entities

### Global
- CREDIT_CARD, CRYPTO, DATE_TIME, EMAIL_ADDRESS, IBAN_CODE
- IP_ADDRESS, NRP, LOCATION, PERSON, PHONE_NUMBER
- MEDICAL_LICENSE, URL

### Country-Specific
- **US**: US_SSN, US_PASSPORT, US_DRIVER_LICENSE, US_BANK_NUMBER, US_ITIN
- **UK**: UK_NHS, UK_NINO
- **Spain**: ES_NIF, ES_NIE
- **Italy**: IT_FISCAL_CODE, IT_DRIVER_LICENSE, IT_VAT_CODE, IT_PASSPORT, IT_IDENTITY_CARD
- **Others**: PL_PESEL, SG_NRIC_FIN, AU_ABN, IN_AADHAAR, FI_PERSONAL_IDENTITY_CODE, KR_RRN, TH_TNIN
- And many more...

## Anonymization Operators

- **replace** - Replace with placeholder or static value
- **redact** - Remove the PII entirely
- **hash** - One-way hash (permanent)
- **mask** - Mask characters with * or other character
- **encrypt** - Reversible encryption
- **keep** - Keep original (for allowlisting)

## Multi-Language Support

Supported languages: en, es, fr, de, it, pt, nl, he, ru, pl, zh, ja, ko, ar, th, fi, and more.

## Best Practices

1. **Test with sample data first** - Validate detection accuracy before production
2. **Use appropriate operators** - Encryption for reversible, hash for permanent
3. **Consider context** - Use context-aware recognizers for better accuracy
4. **Secure encryption keys** - Store keys securely, never hardcode
5. **Handle multiple languages** - Specify correct language code
6. **Validate results** - Review confidence scores and false positives
7. **Additional safeguards** - Presidio uses automation; add extra protections in production

## Development

### Adding New Scripts

Add new scripts to `skills/presidio-pii-detection/scripts/`:
1. Create Python script with clear docstring
2. Make it executable: `chmod +x script.py`
3. Add usage examples in comments
4. Update this README

### Adding New References

Add new reference documents to `skills/presidio-pii-detection/references/`:
1. Create markdown file with clear structure
2. Focus on specific use cases or API details
3. Keep it concise and actionable
4. Update main SKILL.md if needed

## Troubleshooting

**Issue**: "Model 'en_core_web_lg' not found"
```bash
python -m spacy download en_core_web_lg
```

**Issue**: "presidio_analyzer module not found"
```bash
pip install presidio-analyzer presidio-anonymizer
```

**Issue**: Low detection accuracy
- Try using transformers NLP engine
- Lower score_threshold
- Add context words to recognizers
- Use appropriate language code

**Issue**: False positives
- Implement allowlists
- Adjust score_threshold
- Use more specific entity types
- Add context awareness

## License

This plugin and skill follow the same MIT license as the Presidio repository.

## Contributing

To improve or extend these skills:
1. Edit `skills/presidio-pii-detection/SKILL.md` for instruction changes
2. Add scripts to `skills/presidio-pii-detection/scripts/`
3. Add reference docs to `skills/presidio-pii-detection/references/`
4. Update this README
5. Test thoroughly with Claude Code

## Support

For issues with:
- **Presidio Library**: https://github.com/microsoft/presidio/issues
- **This Plugin**: Create an issue in this repository
- **Claude Code**: Follow Claude Code documentation

## Version History

- **1.0.0** (2025-01-XX) - Initial release
  - Comprehensive PII detection skill
  - Text analysis and anonymization scripts
  - API quick reference
  - Multi-language support
  - Custom recognizer examples
