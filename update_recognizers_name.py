#!/usr/bin/env python3
"""Script to update recognizer __init__ methods to explicitly handle name parameter."""

import re
from pathlib import Path

recognizer_files = [
    "presidio_analyzer/predefined_recognizers/country_specific/india/in_pan_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/india/in_passport_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/india/in_vehicle_registration_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/india/in_gstin_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/india/in_aadhaar_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/india/in_voter_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/italy/it_fiscal_code_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/italy/it_passport_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/italy/it_identity_card_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/italy/it_driver_license_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/poland/pl_pesel_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/finland/fi_personal_identity_code_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/singapore/sg_fin_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/singapore/sg_uen_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/korea/kr_rrn_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/australia/au_tfn_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/australia/au_abn_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/australia/au_medicare_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/australia/au_acn_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/uk/uk_nino_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/uk/uk_nhs_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/spain/es_nie_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/spain/es_nif_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/thai/th_tnin_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/aba_routing_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/us_passport_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/medical_license_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/us_bank_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/us_driver_license_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/us_ssn_recognizer.py",
    "presidio_analyzer/predefined_recognizers/country_specific/us/us_itin_recognizer.py",
    "presidio_analyzer/predefined_recognizers/nlp_engine_recognizers/spacy_recognizer.py",
    "presidio_analyzer/predefined_recognizers/nlp_engine_recognizers/stanza_recognizer.py",
    "presidio_analyzer/predefined_recognizers/nlp_engine_recognizers/transformers_recognizer.py",
    "presidio_analyzer/predefined_recognizers/third_party/azure_openai_langextract_recognizer.py",
    "presidio_analyzer/predefined_recognizers/third_party/ahds_recognizer.py",
    "presidio_analyzer/predefined_recognizers/third_party/langextract_recognizer.py",
    "presidio_analyzer/predefined_recognizers/third_party/ollama_langextract_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/url_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/ip_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/credit_card_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/crypto_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/email_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/phone_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/iban_recognizer.py",
    "presidio_analyzer/predefined_recognizers/generic/date_recognizer.py",
    "presidio_analyzer/predefined_recognizers/ner/gliner_recognizer.py",
]

base_dir = Path("/home/ronsha/vscodeProjects/presidio/presidio-analyzer")


def update_file(file_path: Path):
    """Update a recognizer file to explicitly handle name parameter."""
    with open(file_path, 'r') as f:
        content = f.read()

    original_content = content

    # Check if file already has name parameter explicitly in __init__
    if re.search(r'def __init__\(.*\bname:\s*(?:Optional\[)?str', content, flags=re.DOTALL):
        print(f"Skipping {file_path.name} - already has explicit name parameter")
        return False

    # Pattern 1: Add name parameter before **kwargs in __init__ signature
    # Match __init__ methods with **kwargs parameter
    # We need to find the comma before **kwargs and insert name parameter
    def replace_init_signature(match):
        full_match = match.group(0)
        # Find the last parameter before **kwargs
        # Insert name parameter before **kwargs
        result = re.sub(
            r'(\s*,\s*)(\*\*kwargs)',
            r', name: Optional[str] = None, \2',
            full_match,
            count=1
        )
        return result

    pattern1 = r'def __init__\([^)]*?\*\*kwargs[^)]*?\)'
    content = re.sub(pattern1, replace_init_signature, content, flags=re.DOTALL)

    # Pattern 2: Replace super().__init__(..., **kwargs) with super().__init__(..., name=name)
    # Match super().__init__( ... **kwargs)
    def replace_super_call(match):
        full_match = match.group(0)
        # Replace **kwargs with name=name in super().__init__ call
        result = re.sub(
            r',\s*\*\*kwargs',
            ', name=name',
            full_match,
            count=1
        )
        return result

    pattern2 = r'super\(\).__init__\([^)]*?\*\*kwargs[^)]*?\)'
    content = re.sub(pattern2, replace_super_call, content, flags=re.DOTALL)

    # Add Optional import if not present and we made changes
    if content != original_content:
        if 'from typing import' in content:
            # Check if Optional is already imported
            if not re.search(r'from typing import[^;\n]*\bOptional\b', content):
                # Add Optional to existing typing import
                content = re.sub(
                    r'(from typing import )([^\n]+)',
                    lambda m: f"{m.group(1)}Optional, {m.group(2)}" if ', ' in m.group(2) else f"{m.group(1)}Optional, {m.group(2)}",
                    content,
                    count=1
                )

    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"✓ Updated {file_path.name}")
        return True
    else:
        print(f"○ No changes needed for {file_path.name}")
        return False


def main():
    """Update all recognizer files."""
    updated_count = 0
    for rel_path in recognizer_files:
        file_path = base_dir / rel_path
        if file_path.exists():
            if update_file(file_path):
                updated_count += 1
        else:
            print(f"✗ File not found: {file_path}")

    print(f"\n{'='*60}")
    print(f"Updated {updated_count} out of {len(recognizer_files)} files")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
