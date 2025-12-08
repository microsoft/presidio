#!/usr/bin/env python
"""Benchmark script to compare AnalyzerMode performance with NLP engine inspection."""

import time
import logging
from presidio_analyzer import AnalyzerEngine, AnalyzerMode
from presidio_analyzer import RecognizerResult

# Configure logging - only show warnings and above to reduce noise
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("presidio-analyzer")
logger.setLevel(logging.WARNING)


# Test samples with expected entities (ground truth)
# 11 examples designed to differentiate between spaCy and Transformers models:
# - 2 one-liners (simple cases both should handle)
# - 6 medium (2-3 lines, medical context where Transformers excel)
# - 3 long complex (realistic PHI challenges)
#
# spaCy struggles with: unusual name formats, inverted names, medical context, embedded IDs
# Transformers excel at: healthcare-trained NER, unusual PHI patterns
#
# NOTE: expected_spans can have multiple acceptable entity types for the same text
# using tuples: ("text", ["TYPE1", "TYPE2"]) means either type is acceptable
# This handles cases like "Stanford Medical Center" being detected as ORGANIZATION or LOCATION
TEST_SAMPLES = [
    # ============ ONE-LINERS (2) - Both should handle well ============
    {
        "id": "01_simple_person",
        "text": "My name is John Smith and I live in New York.",
        "expected_spans": [
            # (text, [acceptable_entity_types])
            ("John Smith", ["PERSON"]),
            ("New York", ["LOCATION"]),
        ],
        "description": "One-liner: name + location",
    },
    {
        "id": "02_simple_contact",
        "text": "Contact me at john.smith@email.com or call (555) 123-4567.",
        "expected_spans": [
            ("john.smith@email.com", ["EMAIL_ADDRESS"]),
            ("(555) 123-4567", ["PHONE_NUMBER"]),
        ],
        "description": "One-liner: email + phone",
    },
    
    # ============ MEDIUM (6) - 2-3 lines, medical context ============
    {
        "id": "03_med_inverted_name",
        "text": """Reported by: dr nakamura kenji
Radiologist at Cleveland Clinic Imaging Center.""",
        "expected_spans": [
            ("dr nakamura kenji", ["PERSON"]),
            ("Cleveland Clinic Imaging Center", ["ORGANIZATION", "LOCATION"]),
            ("Cleveland Clinic", ["ORGANIZATION", "LOCATION"]),  # partial match also OK
        ],
        "description": "Medium: inverted name with title",
    },
    {
        "id": "04_med_unusual_name",
        "text": """Scan performed by fatima al-rashid md 847293156 at Cardiology, Mayo.
Any questions please contact the department.""",
        "expected_spans": [
            ("fatima al-rashid md", ["PERSON"]),
            # 847293156 can be detected as ID (transformers) or various US types
            ("847293156", ["ID", "US_PASSPORT", "US_SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE"]),
            ("Mayo", ["ORGANIZATION", "LOCATION", "PERSON"]),
        ],
        "description": "Medium: unusual name + inline ID",
    },
    {
        "id": "05_med_chaperone",
        "text": """Pelvic ultrasound performed following verbal consent.
Chaperoned by lisa nguyen (Medical Assistant present).
No contrast allergy documented.""",
        "expected_spans": [
            ("lisa nguyen", ["PERSON"]),
            # Medical Assistant rarely detected, but accept if found
            ("Medical Assistant", ["ORGANIZATION", "LOCATION"]),
        ],
        "description": "Medium: staff name in parentheses",
    },
    {
        "id": "06_med_patient_ref",
        "text": """I note that Mr. Okonkwo has had MRI Brain on 2024-05-22.
Ordered by the neurology team here at Johns Hopkins Medical Center.""",
        "expected_spans": [
            ("Mr. Okonkwo", ["PERSON"]),
            ("2024-05-22", ["DATE_TIME"]),
            ("Johns Hopkins Medical Center", ["ORGANIZATION", "LOCATION"]),
        ],
        "description": "Medium: patient reference mid-text",
    },
    {
        "id": "07_med_signature",
        "text": """Interpreted and reported by alexandra petrov md FACR.
University of Michigan Radiology #MRN-7842916
Dictated using Dragon Medical One.""",
        "expected_spans": [
            ("alexandra petrov md", ["PERSON"]),
            ("alexandra petrov", ["PERSON"]),  # spaCy may split
            ("University of Michigan Radiology", ["ORGANIZATION", "LOCATION"]),
            ("University of Michigan", ["ORGANIZATION", "LOCATION"]),  # partial OK
            ("7842916", ["ID", "US_DRIVER_LICENSE", "MEDICAL_LICENSE"]),
            ("MRN-7842916", ["ID"]),
        ],
        "description": "Medium: signature block with ID",
    },
    {
        "id": "08_med_ids_mixed",
        "text": """Patient MRN: 924817653
Accession: #RAD-XK7829
NPI: 1928374650
Contact: imaging.dept@cedars-sinai.org""",
        "expected_spans": [
            ("924817653", ["ID", "US_PASSPORT", "US_SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE"]),
            ("RAD-XK7829", ["ID"]),
            ("#RAD-XK7829", ["ID"]),  # with hash
            ("1928374650", ["ID", "US_PASSPORT", "US_SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE", "NPI_NUMBER"]),
            ("imaging.dept@cedars-sinai.org", ["EMAIL_ADDRESS"]),
        ],
        "description": "Medium: multiple ID formats",
    },
    
    # ============ LONG COMPLEX (3) - Realistic PHI challenges ============
    {
        "id": "09_long_ultrasound",
        "text": """IMPRESSION:
Viable, singleton intrauterine pregnancy at 31w3d, with a calculated EDD of 2024-08-20 and estimated fetal weight of 2,087 g

For review in Maternal-Fetal Medicine.

Scan performed by fatima al-rashid md 847293156 at OB/GYN, Northwestern.

Reported by: dr nakamura kenji
Senior Sonographer
Midwest Women's Health Partners LLC
Staff ID: 847293156
Ref #RAD-XK7829

For questions contact mfm.support@nwhealth.edu or call 312-555-8847""",
        "expected_spans": [
            ("fatima al-rashid md", ["PERSON"]),
            ("dr nakamura kenji", ["PERSON"]),
            ("2024-08-20", ["DATE_TIME"]),
            ("847293156", ["ID", "US_PASSPORT", "US_SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE"]),
            ("RAD-XK7829", ["ID"]),
            ("#RAD-XK7829", ["ID"]),
            ("Midwest Women's Health Partners LLC", ["ORGANIZATION", "LOCATION"]),
            ("Northwestern", ["ORGANIZATION", "LOCATION", "PERSON"]),
            ("mfm.support@nwhealth.edu", ["EMAIL_ADDRESS"]),
            ("312-555-8847", ["PHONE_NUMBER"]),
        ],
        "description": "Long: ultrasound report with PHI",
    },
    {
        "id": "10_long_discharge",
        "text": """DISCHARGE SUMMARY
Patient: Marcus Jerome Williams
DOB: 11/03/1965
SSN: 287-54-9183
Email: m.williams.home@gmail.com
Phone: (404) 555-2847

Admitted: 2024-06-10
Discharged: 2024-06-15
Facility: Emory University Hospital

Attending Physician: Dr. Priya Sharma, MD
License #: GA-MD-582947

Follow-up appointment scheduled with Dr. Sharma on 2024-06-29.""",
        "expected_spans": [
            ("Marcus Jerome Williams", ["PERSON"]),
            ("Dr. Priya Sharma", ["PERSON"]),
            ("Dr. Priya Sharma, MD", ["PERSON"]),  # with MD suffix
            ("Priya Sharma", ["PERSON"]),  # without Dr
            ("Dr. Sharma", ["PERSON"]),  # follow-up mention
            ("07/22/1958", ["DATE_TIME"]),
            ("2024-02-15", ["DATE_TIME"]),
            ("2024-02-20", ["DATE_TIME"]),
            ("2024-03-01", ["DATE_TIME"]),
            ("456-78-9012", ["US_SSN"]),
            ("robert.thompson@email.com", ["EMAIL_ADDRESS"]),
            ("(617) 555-8901", ["PHONE_NUMBER"]),
            ("Boston General Hospital", ["ORGANIZATION", "LOCATION"]),
            ("MA-12345678", ["ID", "MEDICAL_LICENSE", "US_DRIVER_LICENSE"]),
            ("12345678", ["ID", "US_DRIVER_LICENSE", "US_BANK_NUMBER"]),  # without prefix
        ],
        "description": "Long: discharge summary full PHI",
    },
    {
        "id": "11_long_demo",
        "text": """Here are a few examples sentences we currently support:

Hello, my name is Hiroshi Tanaka and I live in Portland, Oregon.
My credit card number is 4095-2609-9393-4932 and my crypto wallet id is 16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ.

On September 18 I visited acmecorp.com and sent an email to support@healthportal.io, from IP 192.168.0.1.

My passport: 547821936 and my phone number: (503) 555-7291.

This is a valid International Bank Account Number: DE89370400440532013000. Can you please check the status on bank account 954567876544?

Svetlana's social security number is 078-05-1126. Her driver license? it is 1234567A.


This project welcomes contributions and suggestions. Most contributions require you to agree to a Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us the rights to use your contribution. For details, visit https://opensource.example.com
When you submit a pull request, a CLA-bot will automatically determine whether you need to provide a CLA and decorate the PR appropriately (e.g., label, comment).
Simply follow the instructions provided by the bot. You will only need to do this once across all repos using our CLA.
This project has adopted the Example Corp Open Source Code of Conduct.

For more information see the Code of Conduct FAQ or contact legal@examplecorp.com with any additional questions or comments.""",
        "expected_spans": [
            ("Hiroshi Tanaka", ["PERSON"]),
            ("Svetlana", ["PERSON"]),
            ("Portland, Oregon", ["LOCATION"]),
            ("Portland", ["LOCATION"]),
            ("Oregon", ["LOCATION"]),
            ("4095-2609-9393-4932", ["CREDIT_CARD"]),
            ("16Yeky6GMjeNkAiNcBY7ZhrLoMSgg1BoyZ", ["CRYPTO"]),
            ("September 18", ["DATE_TIME"]),
            ("acmecorp.com", ["URL", "ORGANIZATION"]),
            ("https://opensource.example.com", ["URL"]),
            ("support@healthportal.io", ["EMAIL_ADDRESS"]),
            ("legal@examplecorp.com", ["EMAIL_ADDRESS"]),
            ("192.168.0.1", ["IP_ADDRESS"]),
            ("547821936", ["US_PASSPORT", "ID", "US_SSN", "US_BANK_NUMBER", "US_DRIVER_LICENSE"]),
            ("(503) 555-7291", ["PHONE_NUMBER"]),
            ("DE89370400440532013000", ["IBAN_CODE", "ID"]),
            ("954567876544", ["US_BANK_NUMBER", "ID", "US_DRIVER_LICENSE"]),
            ("078-05-1126", ["US_SSN"]),
            ("1234567A", ["US_DRIVER_LICENSE", "ID"]),
        ],
        "description": "Long: comprehensive demo with many entity types",
    },
    {
        "id": "13_age_over_89_numeric",
        "text": "Patient age: 95. Admitted for cardiac evaluation. Blood pressure 140/90.",
        "expected_spans": [
            ("95", ["AGE", "GENERIC_PII_ENTITY"]),
        ],
        "description": "LLM-only: numeric age over 89",
    },
    {
        "id": "14_age_centenarian",
        "text": "Mrs. Rosalind Beaumont, age 101, presents with mild cognitive impairment. She was born in 1923.",
        "expected_spans": [
            ("Mrs. Rosalind Beaumont", ["PERSON"]),
            ("Rosalind Beaumont", ["PERSON"]),
            ("101", ["AGE", "GENERIC_PII_ENTITY"]),
            ("1923", ["DATE_TIME"]),
        ],
        "description": "LLM-only: centenarian with name",
    },
    {
        "id": "15_age_mixed_report",
        "text": """GERIATRIC ASSESSMENT
Patient: 94-year-old male
Referred by: Dr. Adaora Nwosu, MD
Facility: Lakewood Memory Care Center
Contact: intake@lakewoodmemory.org

The patient, a 94-year-old retired engineer, was evaluated for memory concerns.
His daughter, age 65, accompanies him to appointments.""",
        "expected_spans": [
            ("94-year-old", ["AGE", "GENERIC_PII_ENTITY"]),
            ("94-year-old male", ["AGE", "GENERIC_PII_ENTITY"]),
            ("Dr. Adaora Nwosu", ["PERSON"]),
            ("Dr. Adaora Nwosu, MD", ["PERSON"]),
            ("Adaora Nwosu", ["PERSON"]),
            ("Lakewood Memory Care Center", ["ORGANIZATION", "LOCATION"]),
            ("intake@lakewoodmemory.org", ["EMAIL_ADDRESS"]),
            # Note: age 65 is NOT PHI under HIPAA (only 90+ is identifiable)
        ],
        "description": "LLM-only: geriatric report with 90+ age",
    },
]


def inspect_nlp_engine(analyzer: AnalyzerEngine, mode_name: str):
    """Inspect and print details about the NLP engine being used."""
    nlp_engine = analyzer.nlp_engine
    engine_class = nlp_engine.__class__.__name__
    
    print(f"\n{'='*70}")
    print(f"NLP Engine Inspection for {mode_name}")
    print(f"{'='*70}")
    print(f"  Engine Class: {engine_class}")
    
    transformer_model_found = None
    
    if hasattr(nlp_engine, 'nlp') and nlp_engine.nlp:
        for lang, pipeline in nlp_engine.nlp.items():
            print(f"  Language: {lang}")
            print(f"    spaCy Pipeline: {pipeline.meta.get('name', 'unknown')}")
            print(f"    Components: {pipeline.pipe_names}")
            
            # Look for transformer/huggingface component
            for comp_name in pipeline.pipe_names:
                if 'hf_token_pipe' in comp_name or 'transformer' in comp_name.lower():
                    try:
                        component = pipeline.get_pipe(comp_name)
                        # Try multiple ways to get model info
                        if hasattr(component, 'model'):
                            model = component.model
                            if hasattr(model, 'config'):
                                config = model.config
                                if hasattr(config, '_name_or_path'):
                                    transformer_model_found = config._name_or_path
                                elif hasattr(config, 'name_or_path'):
                                    transformer_model_found = config.name_or_path
                        # Check for model_name attribute
                        if not transformer_model_found and hasattr(component, 'name'):
                            transformer_model_found = component.name
                    except Exception as e:
                        print(f"    (Could not inspect {comp_name}: {e})")
    
    # Check for transformers-specific attributes
    if hasattr(nlp_engine, 'ner_model_configuration'):
        config = nlp_engine.ner_model_configuration
        print(f"  NER Model Configuration:")
        print(f"    Aggregation Strategy: {getattr(config, 'aggregation_strategy', 'N/A')}")
        print(f"    Alignment Mode: {getattr(config, 'alignment_mode', 'N/A')}")
        if hasattr(config, 'model_to_presidio_entity_mapping'):
            mappings = config.model_to_presidio_entity_mapping
            print(f"    Entity Mappings: {len(mappings)} types")
    
    # Report transformer status
    if engine_class == "TransformersNlpEngine":
        print(f"\n  ✓ CONFIRMED: Using Transformers NLP Engine")
        # Get model from nlp_engine.models (the config)
        if hasattr(nlp_engine, 'models') and nlp_engine.models:
            for m in nlp_engine.models:
                if isinstance(m, dict) and 'model_name' in m:
                    model_name = m.get('model_name', {})
                    if isinstance(model_name, dict):
                        if 'transformers' in model_name:
                            print(f"  ✓ Transformer Model: {model_name['transformers']}")
                        if 'spacy' in model_name:
                            print(f"    spaCy tokenizer: {model_name['spacy']}")
    elif engine_class == "SpacyNlpEngine":
        print(f"\n  ✓ CONFIRMED: Using spaCy NLP Engine (no transformers)")
    
    print(f"{'='*70}\n")
    
    return {"engine_class": engine_class, "transformer_model": transformer_model_found}


def inspect_recognizers(analyzer: AnalyzerEngine):
    """List all recognizers in the analyzer registry."""
    print("  Registered Recognizers:")
    recognizer_names = [r.name for r in analyzer.registry.recognizers]
    # Group by type
    nlp_recognizers = [n for n in recognizer_names if 'Spacy' in n or 'Transformers' in n]
    pattern_recognizers = [n for n in recognizer_names if n not in nlp_recognizers]
    
    print(f"    NLP-based ({len(nlp_recognizers)}): {', '.join(nlp_recognizers)}")
    print(f"    Pattern-based ({len(pattern_recognizers)}): {len(pattern_recognizers)} recognizers")
    return recognizer_names


def normalize_text(text: str) -> str:
    """Normalize text for comparison (strip whitespace, lowercase)."""
    return text.strip().lower()


def calculate_span_metrics(results: list, text: str, expected_spans: list):
    """
    Calculate precision, recall, and F1 score based on actual text spans.
    Supports alternative entity types for the same span.
    
    Args:
        results: List of RecognizerResult objects from analyzer
        text: The original text that was analyzed
        expected_spans: List of tuples: [(text, [acceptable_types]), ...]
    
    Returns:
        Dict with precision, recall, f1, tp, fp, fn, matches, missed, extra
    """
    # Build detected spans: {normalized_text: set of entity_types detected}
    detected_by_text = {}
    detected_details = []
    for r in results:
        detected_text = normalize_text(text[r.start:r.end])
        if detected_text not in detected_by_text:
            detected_by_text[detected_text] = set()
        detected_by_text[detected_text].add(r.entity_type)
        detected_details.append({
            "entity_type": r.entity_type,
            "text": text[r.start:r.end],
            "score": r.score,
            "start": r.start,
            "end": r.end,
        })
    
    # Build expected spans lookup: {normalized_text: set of acceptable_types}
    expected_by_text = {}
    for expected_text, acceptable_types in expected_spans:
        norm_text = normalize_text(expected_text)
        if norm_text not in expected_by_text:
            expected_by_text[norm_text] = set()
        expected_by_text[norm_text].update(acceptable_types)
    
    # Track matches, misses
    matches = []  # (text, matched_type)
    missed = []   # (text, acceptable_types)
    matched_detections = set()  # (normalized_text, entity_type) pairs that matched
    
    # For each expected span, check if ANY acceptable type was detected
    matched_expected = set()
    for expected_text, acceptable_types in expected_spans:
        norm_text = normalize_text(expected_text)
        if norm_text in matched_expected:
            continue  # Already matched this text in a previous entry
            
        found = False
        if norm_text in detected_by_text:
            # Check if any detected type matches acceptable types
            for detected_type in detected_by_text[norm_text]:
                if detected_type in acceptable_types:
                    matches.append((expected_text, detected_type))
                    matched_detections.add((norm_text, detected_type))
                    found = True
                    matched_expected.add(norm_text)
                    break  # One match per expected span text
        
        if not found and norm_text not in matched_expected:
            missed.append((expected_text, acceptable_types))
    
    # Find extra/false positives (detections that didn't match expectations)
    # Logic: If a span has at least one acceptable type, don't penalize extra labels
    extra = []
    for norm_text, detected_types in detected_by_text.items():
        acceptable_for_this_text = expected_by_text.get(norm_text, set())

        if not acceptable_for_this_text:
            # This text wasn't expected at all -> all detections are FPs
            for dtype in detected_types:
                extra.append((norm_text, dtype))
            continue

        # Text is expected. If ANY detected type is acceptable,
        # we treat the whole span as a hit and DO NOT penalize extra labels.
        if detected_types & acceptable_for_this_text:
            # There's at least one correct type -> ignore extra types for FP counting
            continue

        # Text is expected but none of the detected types are acceptable -> all are FPs
        for dtype in detected_types:
            extra.append((norm_text, dtype))
    
    tp = len(matches)
    fp = len(extra)
    fn = len(missed)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "matches": matches,
        "missed": missed,
        "extra": extra,
        "detected_details": detected_details,
    }


def benchmark_mode(mode: AnalyzerMode, mode_name: str):
    """Benchmark a specific analyzer mode."""
    print(f"\n{'#'*70}")
    print(f"# Benchmarking: {mode_name}")
    print(f"{'#'*70}")
    
    # Initialize analyzer
    start_init = time.time()
    analyzer = AnalyzerEngine(mode=mode)
    init_time = time.time() - start_init
    print(f"Initialization time: {init_time*1000:.1f}ms")
    
    # Inspect the NLP engine
    engine_info = inspect_nlp_engine(analyzer, mode_name)
    
    # Inspect recognizers
    inspect_recognizers(analyzer)
    
    # Run analysis on all samples
    total_time = 0
    all_tp, all_fp, all_fn = 0, 0, 0
    
    print(f"\n{'ID':<12} {'Time':>8} {'P':>6} {'R':>6} {'F1':>6} {'Description':<30}")
    print("-" * 80)
    
    detailed_results = []
    
    for sample in TEST_SAMPLES:
        sample_id = sample.get("id", "unknown")
        text = sample["text"]
        expected_spans = sample.get("expected_spans", [])
        description = sample.get("description", "")[:28]
        
        start = time.time()
        results = analyzer.analyze(text=text, language="en")
        elapsed = time.time() - start
        total_time += elapsed
        
        # Calculate span-based metrics
        metrics = calculate_span_metrics(results, text, expected_spans)
        
        all_tp += metrics["tp"]
        all_fp += metrics["fp"]
        all_fn += metrics["fn"]
        
        match = "✓" if metrics["fn"] == 0 else "✗"
        
        print(f"  {sample_id:<10} {elapsed*1000:>6.0f}ms {metrics['precision']*100:>5.0f}% {metrics['recall']*100:>5.0f}% {metrics['f1']*100:>5.0f}% {description:<30} {match}")
        
        # Store detailed info for later
        detailed_results.append({
            "id": sample_id,
            "metrics": metrics,
            "time_ms": elapsed * 1000,
            "results": results,
        })
    
    print("-" * 80)
    
    # Show what was detected vs expected
    print(f"\n  === DETECTION DETAILS ===")
    for dr in detailed_results:
        print(f"\n  [{dr['id']}]")
        
        # Show what was correctly matched
        if dr["metrics"]["matches"]:
            print(f"    ✓ MATCHED ({len(dr['metrics']['matches'])}):")
            for text, matched_type in sorted(dr["metrics"]["matches"], key=lambda x: x[0].lower()):
                print(f"        {matched_type}: \"{text}\"")
        
        # Show what was missed (false negatives)
        if dr["metrics"]["missed"]:
            print(f"    ✗ MISSED ({len(dr['metrics']['missed'])}):")
            for text, acceptable_types in sorted(dr["metrics"]["missed"], key=lambda x: x[0].lower()):
                types_str = "|".join(acceptable_types)
                print(f"        [{types_str}]: \"{text}\"")
        
        # Show extra detections (false positives) 
        if dr["metrics"]["extra"]:
            print(f"    ⚠ EXTRA/FP ({len(dr['metrics']['extra'])}):")
            for text, entity_type in sorted(dr["metrics"]["extra"]):
                print(f"        {entity_type}: \"{text}\"")
        
        # Show all detections with scores
        print(f"    📋 ALL DETECTIONS ({len(dr['metrics']['detected_details'])}):")
        for det in sorted(dr["metrics"]["detected_details"], key=lambda x: x["start"]):
            print(f"        [{det['start']:4d}-{det['end']:4d}] {det['entity_type']:<15} ({det['score']:.2f}): \"{det['text'][:50]}\"{'...' if len(det['text']) > 50 else ''}")
    
    # Show which recognizers detected what
    print(f"\n  === RECOGNIZER USAGE ===")
    recognizer_counts = {}
    for dr in detailed_results:
        for result in dr["results"]:
            if result.recognition_metadata:
                rec_name = result.recognition_metadata.get(
                    RecognizerResult.RECOGNIZER_NAME_KEY, "Unknown"
                )
                if rec_name not in recognizer_counts:
                    recognizer_counts[rec_name] = 0
                recognizer_counts[rec_name] += 1
    
    for rec_name, count in sorted(recognizer_counts.items(), key=lambda x: -x[1]):
        print(f"    {rec_name}: {count} detections")
    
    # Calculate overall metrics
    precision = all_tp / (all_tp + all_fp) if (all_tp + all_fp) > 0 else 0
    recall = all_tp / (all_tp + all_fn) if (all_tp + all_fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    
    print("-" * 80)
    print(f"\n{mode_name} SUMMARY:")
    print(f"  Total Time: {total_time*1000:.1f}ms (avg: {total_time*1000/len(TEST_SAMPLES):.1f}ms per sample)")
    print(f"  Precision: {precision*100:.2f}%")
    print(f"  Recall: {recall*100:.2f}%")
    print(f"  F1 Score: {f1*100:.2f}%")
    print(f"  True Positives: {all_tp}, False Positives: {all_fp}, False Negatives: {all_fn}")
    
    return {
        "mode": mode_name,
        "init_time": init_time * 1000,
        "total_time": total_time * 1000,
        "avg_time": total_time * 1000 / len(TEST_SAMPLES),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": all_tp,
        "fp": all_fp,
        "fn": all_fn,
    }


def main():
    print("\n" + "=" * 70)
    print(" PRESIDIO ANALYZER MODE BENCHMARK")
    print(" Comparing FAST, BALANCED, and ACCURATE modes")
    print("=" * 70)
    
    # Initialize all analyzers first
    modes_config = [
        (AnalyzerMode.FAST, "FAST"),
        (AnalyzerMode.BALANCED, "BALANCED"),
        (AnalyzerMode.ACCURATE, "ACCURATE"),
    ]
    
    analyzers = {}
    for mode, name in modes_config:
        print(f"\nLoading {name}...")
        start = time.time()
        analyzers[name] = AnalyzerEngine(mode=mode)
        print(f"  Initialized in {(time.time()-start)*1000:.0f}ms")
    
    # Run all samples and collect results per mode
    all_results = {name: [] for name in analyzers.keys()}
    failed_modes = set()
    
    print("\n" + "=" * 70)
    print(" RUNNING ANALYSIS ON ALL SAMPLES")
    print("=" * 70)
    
    for sample in TEST_SAMPLES:
        sample_id = sample.get("id", "unknown")
        text = sample["text"]
        expected_spans = sample.get("expected_spans", [])
        
        for mode_name, analyzer in analyzers.items():
            if mode_name in failed_modes:
                # Skip failed modes for remaining samples
                all_results[mode_name].append({
                    "id": sample_id,
                    "text": text,
                    "expected_spans": expected_spans,
                    "results": [],
                    "metrics": {"precision": 0, "recall": 0, "f1": 0, "tp": 0, "fp": 0, "fn": len(expected_spans)},
                    "error": True,
                })
                continue
                
            try:
                results = analyzer.analyze(text=text, language="en")
                metrics = calculate_span_metrics(results, text, expected_spans)
                all_results[mode_name].append({
                    "id": sample_id,
                    "text": text,
                    "expected_spans": expected_spans,
                    "results": results,
                    "metrics": metrics,
                })
            except Exception as e:
                print(f"\n  ⚠ {mode_name} failed on sample {sample_id}: {type(e).__name__}")
                failed_modes.add(mode_name)
                all_results[mode_name].append({
                    "id": sample_id,
                    "text": text,
                    "expected_spans": expected_spans,
                    "results": [],
                    "metrics": {"precision": 0, "recall": 0, "f1": 0, "tp": 0, "fp": 0, "fn": len(expected_spans)},
                    "error": True,
                })
    
    if failed_modes:
        print(f"\n  ⚠ Modes with errors (excluded from comparison): {', '.join(failed_modes)}")
    
    # Filter out failed modes for display
    active_modes = [name for name in analyzers.keys() if name not in failed_modes]
    
    # Display results side-by-side per sample
    print("\n" + "=" * 70)
    print(" SIDE-BY-SIDE DETECTION COMPARISON")
    print("=" * 70)
    
    for i, sample in enumerate(TEST_SAMPLES):
        sample_id = sample.get("id", "unknown")
        text = sample["text"]
        description = sample.get("description", "")
        
        print(f"\n{'#'*80}")
        print(f"# SAMPLE: {sample_id} - {description}")
        print(f"{'#'*80}")
        text_preview = text.replace('\n', ' ')[:100]
        print(f"TEXT: {text_preview}{'...' if len(text) > 100 else ''}")
        print()
        
        # Get results for this sample from each mode
        fast_data = all_results["FAST"][i]
        balanced_data = all_results["BALANCED"][i]
        
        # Build detection maps: text -> list of (entity_type, score)
        fast_detections = {}
        for r in fast_data["results"]:
            t = text[r.start:r.end]
            if t not in fast_detections:
                fast_detections[t] = []
            fast_detections[t].append((r.entity_type, r.score))
        
        balanced_detections = {}
        for r in balanced_data["results"]:
            t = text[r.start:r.end]
            if t not in balanced_detections:
                balanced_detections[t] = []
            balanced_detections[t].append((r.entity_type, r.score))
        
        # Combine all detected texts
        all_texts = set(fast_detections.keys()) | set(balanced_detections.keys())
        
        # Sort by position in text
        def get_pos(t):
            pos = text.find(t)
            return pos if pos >= 0 else 9999
        
        print(f"{'DETECTED TEXT':<45} {'FAST (spaCy)':<30} {'BALANCED (Transformers)':<30}")
        print("-" * 105)
        
        for t in sorted(all_texts, key=get_pos):
            t_display = t.replace('\n', '↵')[:43]
            
            fast_types = fast_detections.get(t, [])
            balanced_types = balanced_detections.get(t, [])
            
            # Format as comma-separated entity types
            fast_str = ", ".join(sorted(set(et for et, s in fast_types))) if fast_types else "—"
            balanced_str = ", ".join(sorted(set(et for et, s in balanced_types))) if balanced_types else "—"
            
            # Truncate if too long
            if len(fast_str) > 28:
                fast_str = fast_str[:25] + "..."
            if len(balanced_str) > 28:
                balanced_str = balanced_str[:25] + "..."
            
            # Mark key differences
            marker = ""
            if fast_types and not balanced_types:
                marker = " ◄ FAST only"
            elif balanced_types and not fast_types:
                marker = " ◄ BALANCED only"
            
            print(f"{t_display:<45} {fast_str:<30} {balanced_str:<30}{marker}")
        
        # Show metrics comparison
        print()
        print(f"  FAST:     P={fast_data['metrics']['precision']*100:.0f}%  R={fast_data['metrics']['recall']*100:.0f}%  F1={fast_data['metrics']['f1']*100:.0f}%  (TP={fast_data['metrics']['tp']}, FP={fast_data['metrics']['fp']}, FN={fast_data['metrics']['fn']})")
        print(f"  BALANCED: P={balanced_data['metrics']['precision']*100:.0f}%  R={balanced_data['metrics']['recall']*100:.0f}%  F1={balanced_data['metrics']['f1']*100:.0f}%  (TP={balanced_data['metrics']['tp']}, FP={balanced_data['metrics']['fp']}, FN={balanced_data['metrics']['fn']})")
    
    # Print ALL detections per model (unfiltered)
    print("\n" + "=" * 100)
    print(" ALL DETECTIONS BY MODEL (unfiltered, raw output from each analyzer)")
    print("=" * 100)
    
    for mode_name in analyzers.keys():
        print(f"\n{'─' * 50}")
        print(f" {mode_name} MODE - ALL DETECTIONS")
        print(f"{'─' * 50}")
        
        for i, sample in enumerate(TEST_SAMPLES):
            text = sample["text"]
            results = all_results[mode_name][i]["results"]
            sample_label = sample.get("label", f"Sample {i+1:02d}")
            
            print(f"\n[{sample_label}] ({len(results)} detections)")
            if not results:
                print("  (no entities detected)")
                continue
            
            # Sort by position in text
            sorted_results = sorted(results, key=lambda r: r.start)
            for r in sorted_results:
                detected_text = text[r.start:r.end].replace('\n', '↵')
                if len(detected_text) > 40:
                    detected_text = detected_text[:37] + "..."
                print(f"  • {r.entity_type:<20} \"{detected_text}\" (score={r.score:.2f}, pos={r.start}-{r.end})")
    
    # Calculate overall metrics
    print("\n" + "=" * 70)
    print(" FINAL SUMMARY")
    print("=" * 70)
    
    print(f"\n{'Mode':<25} {'Precision':>12} {'Recall':>10} {'F1':>10} {'TP':>6} {'FP':>6} {'FN':>6}")
    print("-" * 80)
    
    for mode_name in analyzers.keys():
        total_tp = sum(r["metrics"]["tp"] for r in all_results[mode_name])
        total_fp = sum(r["metrics"]["fp"] for r in all_results[mode_name])
        total_fn = sum(r["metrics"]["fn"] for r in all_results[mode_name])
        
        precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0
        recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        print(f"{mode_name:<25} {precision*100:>10.1f}% {recall*100:>8.1f}% {f1*100:>8.1f}% {total_tp:>6} {total_fp:>6} {total_fn:>6}")


if __name__ == "__main__":
    main()
