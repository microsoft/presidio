"""Generate a 10-record CSV dataset with correctly positioned PII entities."""

import csv
import json
import os

RECORDS = [
    {
        "text": "Patient John Smith was admitted on 03/15/2025 with diagnosis code A09.",
        "entities": [
            {"text": "John Smith", "type": "PERSON"},
            {"text": "03/15/2025", "type": "DATE_TIME"},
        ],
    },
    {
        "text": "Contact Dr. Emily Chen at emily.chen@hospital.org or call 555-987-6543.",
        "entities": [
            {"text": "Emily Chen", "type": "PERSON"},
            {"text": "emily.chen@hospital.org", "type": "EMAIL_ADDRESS"},
            {"text": "555-987-6543", "type": "PHONE_NUMBER"},
        ],
    },
    {
        "text": "SSN 123-45-6789 belongs to Maria Garcia, born on January 12, 1990.",
        "entities": [
            {"text": "123-45-6789", "type": "US_SSN"},
            {"text": "Maria Garcia", "type": "PERSON"},
            {"text": "January 12, 1990", "type": "DATE_TIME"},
        ],
    },
    {
        "text": "The patient resides at 742 Evergreen Terrace, Springfield, IL 62704.",
        "entities": [
            {"text": "742 Evergreen Terrace, Springfield, IL 62704", "type": "LOCATION"},
        ],
    },
    {
        "text": "Credit card number 4111-1111-1111-1111 was used by Robert Johnson on 12/01/2024.",
        "entities": [
            {"text": "4111-1111-1111-1111", "type": "CREDIT_CARD"},
            {"text": "Robert Johnson", "type": "PERSON"},
            {"text": "12/01/2024", "type": "DATE_TIME"},
        ],
    },
    {
        "text": "Please send records to Sarah Williams at 1600 Pennsylvania Ave, Washington DC 20500.",
        "entities": [
            {"text": "Sarah Williams", "type": "PERSON"},
            {"text": "1600 Pennsylvania Ave, Washington DC 20500", "type": "LOCATION"},
        ],
    },
    {
        "text": "Driver's license D1234567 issued to James Brown, DOB 07/04/1985.",
        "entities": [
            {"text": "D1234567", "type": "US_DRIVER_LICENSE"},
            {"text": "James Brown", "type": "PERSON"},
            {"text": "07/04/1985", "type": "DATE_TIME"},
        ],
    },
    {
        "text": "Insurance ID BC-9876543 for patient Lisa Anderson, phone 202-555-0147.",
        "entities": [
            {"text": "BC-9876543", "type": "MEDICAL_LICENSE"},
            {"text": "Lisa Anderson", "type": "PERSON"},
            {"text": "202-555-0147", "type": "PHONE_NUMBER"},
        ],
    },
    {
        "text": "Lab results for Michael Davis (MRN 00112233) were sent to m.davis@gmail.com.",
        "entities": [
            {"text": "Michael Davis", "type": "PERSON"},
            {"text": "00112233", "type": "US_BANK_NUMBER"},
            {"text": "m.davis@gmail.com", "type": "EMAIL_ADDRESS"},
        ],
    },
    {
        "text": "Nurse Jennifer Lee noted blood pressure 140/90 for patient at 55 Oak Street, Boston MA 02108.",
        "entities": [
            {"text": "Jennifer Lee", "type": "PERSON"},
            {"text": "55 Oak Street, Boston MA 02108", "type": "LOCATION"},
        ],
    },
]


def build_entity(text: str, entity_text: str, entity_type: str) -> dict:
    """Find entity_text in text and return a fully populated entity dict."""
    start = text.index(entity_text)
    return {
        "text": entity_text,
        "entity_type": entity_type,
        "start": start,
        "end": start + len(entity_text),
        "score": 1.0,
    }


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "sample_medical_records.csv")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "entities"])

        for record in RECORDS:
            text = record["text"]
            entities = []
            for ent in record["entities"]:
                entities.append(build_entity(text, ent["text"], ent["type"]))
            writer.writerow([text, json.dumps(entities)])

    abs_path = os.path.abspath(out_path)
    print(f"Created {len(RECORDS)} records at:\n{abs_path}")

    # Verify by reading back
    with open(out_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            ents = json.loads(row["entities"])
            print(f"  [{i+1}] {row['text'][:60]}...  ({len(ents)} entities)")
            for e in ents:
                assert row["text"][e["start"]:e["end"]] == e["text"], \
                    f"Position mismatch: expected '{e['text']}' but got '{row['text'][e['start']:e['end']]}'"
    print("All entity positions verified ✓")


if __name__ == "__main__":
    main()
