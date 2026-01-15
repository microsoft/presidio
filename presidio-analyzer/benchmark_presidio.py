#!/usr/bin/env python3
"""Comprehensive benchmark script for Presidio Analyzer performance testing.

Tests different dataset sizes and NLP engines (spaCy, Transformers, GLiNER).
Generates a markdown report.
"""

import argparse
import json
import logging
import sys
import time
import warnings

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.batch_analyzer_engine import BatchAnalyzerEngine

# Configure logging - suppress presidio-analyzer INFO logs
logging.basicConfig(
    level=logging.ERROR,
    format='%(levelname)s - %(name)s - %(message)s',
    stream=sys.stderr
)

# Suppress warnings from spacy_huggingface_pipelines and other libraries
warnings.filterwarnings('ignore')

# Optional imports for different NLP engines
try:
    from presidio_analyzer.nlp_engine import NlpEngineProvider, TransformersNlpEngine
    from presidio_analyzer.nlp_engine.ner_model_configuration import (
        NerModelConfiguration,
    )
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from presidio_analyzer.predefined_recognizers import GLiNERRecognizer
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False

try:
    from presidio_analyzer.nlp_engine import StanzaNlpEngine
    HAS_STANZA = True
except ImportError:
    HAS_STANZA = False

# Sample texts for testing - large dataset
TEST_TEXT_TEMPLATES = [
    (
        "My name is {name} and my email is {email}. "
        "I work at {company} as a software engineer."
    ),
    "Patient information: Name: {name}, SSN: {ssn}, Phone: {phone}, Address: {address}",
    (
        "Dear {name}, your account {email} has been verified. "
        "Contact us at {phone} for support."
    ),
    "Employee ID: {id}, Name: {name}, Credit Card: {cc}, Expires: {exp_date}",
    "Contact {name} at {phone} or email {email}. Office located at {address}.",
    (
        "Medical record for {name}, born {dob}. "
        "Insurance details: Policy #{id}, contact {phone}."
    ),
    "Transaction approved for {name}. Card ending {cc_last4}. Receipt sent to {email}.",
    (
        "Hello {name}, your appointment at {address} is confirmed "
        "for {date} at {time}. Call {phone} if needed."
    ),
    "User profile: {name}, Username: {email}, Phone: {phone}, Registered: {date}",
    (
        "Billing statement for {name} at {address}. Amount due: $2,500. "
        "Questions? Email {email} or call {phone}."
    ),
    (
        "Dear Dr. {name}, patient consultation scheduled {date}. "
        "Patient contact: {phone}, Address: {address}"
    ),
    (
        "Account #{id} for {name} ({email}) shows activity on {date}. "
        "Security code sent to {phone}."
    ),
    (
        "Prescription refill for {name}, DOB: {dob}. Pharmacy: {address}. "
        "Insurance verification needed, call {phone}."
    ),
    (
        "Welcome {name}! Your credit card {cc} has been added. "
        "Billing address: {address}. Contact: {email}"
    ),
    (
        "Invoice #{id} - {name}, {company}. Payment to {address}. "
        "Due {date}. Support: {email}/{phone}"
    ),
]

NAMES = [
    "John Smith",
    "Sarah Johnson",
    "Michael Brown",
    "Emily Davis",
    "James Wilson",
    "Jessica Martinez",
    "David Anderson",
    "Jennifer Taylor",
    "Robert Thomas",
    "Mary Garcia",
    "Christopher Lee",
    "Patricia Rodriguez",
    "Daniel White",
    "Linda Harris",
    "Matthew Clark",
    "Barbara Lewis",
    "Joseph Walker",
    "Susan Hall",
    "Charles Allen",
    "Karen Young",
]

EMAILS = [
    "john.smith@example.com",
    "sarah.j@company.org",
    "mbrown@corp.net",
    "emily.davis@mail.com",
    "jwilson@business.io",
    "jmartinez@enterprise.com",
    "david.a@startup.tech",
    "jtaylor@firm.law",
    "rthomas@clinic.med",
    "mgarcia@university.edu",
    "clee@consulting.biz",
    "prodriguez@agency.gov",
    "dwhite@financial.com",
    "lharris@retail.store",
    "mclark@manufacturing.ind",
    "blewis@services.pro",
    "jwalker@healthcare.org",
    "shall@education.edu",
    "callen@technology.io",
    "kyoung@pharma.com",
]

PHONES = [
    "555-123-4567",
    "555-234-5678",
    "555-345-6789",
    "555-456-7890",
    "555-567-8901",
    "+1-555-678-9012",
    "+1-202-555-0173",
    "555-789-0123",
    "555-890-1234",
    "555-901-2345",
    "+1-415-555-0198",
    "+1-310-555-0142",
    "555-111-2222",
    "555-222-3333",
    "555-333-4444",
    "+1-713-555-0156",
    "+1-617-555-0187",
    "555-444-5555",
    "555-555-6666",
    "555-666-7777",
]

SSNS = [
    "123-45-6789", "234-56-7890", "345-67-8901", "456-78-9012", "567-89-0123",
    "678-90-1234", "789-01-2345", "890-12-3456", "901-23-4567", "012-34-5678",
    "111-22-3333", "222-33-4444", "333-44-5555", "444-55-6666", "555-66-7777",
    "666-77-8888", "777-88-9999", "888-99-0000", "999-00-1111", "000-11-2222"
]

ADDRESSES = [
    "123 Main St, New York, NY 10001", "456 Oak Ave, Los Angeles, CA 90012",
    "789 Pine Rd, Chicago, IL 60601", "321 Elm St, Houston, TX 77001",
    "654 Maple Dr, Phoenix, AZ 85001", "987 Cedar Ln, Philadelphia, PA 19101",
    "147 Birch Way, San Antonio, TX 78201", "258 Spruce Ct, San Diego, CA 92101",
    "369 Willow Pl, Dallas, TX 75201", "741 Ash Blvd, San Jose, CA 95101",
    "852 Hickory St, Austin, TX 78701", "963 Walnut Ave, Jacksonville, FL 32099",
    "159 Chestnut Rd, Fort Worth, TX 76101", "357 Magnolia Dr, Columbus, OH 43004",
    "486 Sycamore Ln, Charlotte, NC 28201"
]

CREDIT_CARDS = [
    "4532-1234-5678-9010", "5425-2345-6789-0123", "3782-345678-90123",
    "6011-4567-8901-2345", "3056-567890-1234", "4916-6789-0123-4567",
    "5412-7890-1234-5678", "3714-890123-45678", "6011-9012-3456-7890"
]

DATES = [
    "01/15/2024", "02/20/2024", "03/25/2024", "04/10/2024", "05/18/2024",
    "06/22/2024", "07/30/2024", "08/14/2024", "09/05/2024", "10/12/2024",
    "11/28/2024", "12/31/2024"
]

TIMES = [
    "10:30 AM",
    "2:15 PM",
    "9:00 AM",
    "4:45 PM",
    "11:20 AM",
    "3:30 PM",
    "8:15 AM",
]
DOBS = [
    "05/15/1985",
    "08/22/1990",
    "03/10/1978",
    "11/05/1982",
    "07/30/1995",
    "12/18/1988",
]


def generate_test_texts(count):
    """Generate test texts with PII."""
    texts = []
    for i in range(count):
        template = TEST_TEXT_TEMPLATES[i % len(TEST_TEXT_TEMPLATES)]
        text = template.format(
            name=NAMES[i % len(NAMES)],
            email=EMAILS[i % len(EMAILS)],
            phone=PHONES[i % len(PHONES)],
            ssn=SSNS[i % len(SSNS)],
            address=ADDRESSES[i % len(ADDRESSES)],
            company=f"Company{i % 50}",
            id=f"EMP{10000 + i}",
            cc=CREDIT_CARDS[i % len(CREDIT_CARDS)],
            cc_last4=str(1000 + i % 9000),
            exp_date=DATES[i % len(DATES)],
            date=DATES[i % len(DATES)],
            time=TIMES[i % len(TIMES)],
            dob=DOBS[i % len(DOBS)],
        )
        texts.append(text)
    return texts


def create_transformers_analyzer():
    """Create an analyzer with Transformers NLP engine."""
    if not HAS_TRANSFORMERS:
        raise ImportError(
            "Transformers support not available. "
            "Install with: pip install 'presidio-analyzer[transformers]'"
        )

    # Use simple configuration (same as previous working version)
    # This gives better performance than loading from config file
    model_config = [{
        "lang_code": "en",
        "model_name": {
            "spacy": "en_core_web_sm",
            "transformers": "StanfordAIMI/stanford-deidentifier-base"
        }
    }]

    # Entity mapping from official transformers.yaml config
    mapping = {
        "PER": "PERSON",
        "PERSON": "PERSON",
        "LOC": "LOCATION",
        "LOCATION": "LOCATION",
        "GPE": "LOCATION",
        "ORG": "ORGANIZATION",
        "ORGANIZATION": "ORGANIZATION",
        "NORP": "NRP",
        "AGE": "AGE",
        "ID": "ID",
        "EMAIL": "EMAIL",
        "PATIENT": "PERSON",
        "STAFF": "PERSON",
        "HOSP": "ORGANIZATION",
        "PATORG": "ORGANIZATION",
        "DATE": "DATE_TIME",
        "TIME": "DATE_TIME",
        "PHONE": "PHONE_NUMBER",
        "HCW": "PERSON",
        "HOSPITAL": "LOCATION",
        "FACILITY": "LOCATION",
        "VENDOR": "ORGANIZATION",
    }

    ner_model_configuration = NerModelConfiguration(
        model_to_presidio_entity_mapping=mapping,
        alignment_mode="strict",  # faster than expand
        aggregation_strategy="simple",  # faster than max
        labels_to_ignore=["O"]
    )

    nlp_engine = TransformersNlpEngine(
        models=model_config,
        ner_model_configuration=ner_model_configuration
    )

    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])


def create_gliner_analyzer():
    """Create an analyzer with GLiNER recognizer."""
    if not HAS_GLINER:
        raise ImportError(
            "GLiNER support not available. "
            "Install with: pip install 'presidio-analyzer[gliner]'"
        )

    # Use small spaCy model (we don't need spaCy's NER)
    nlp_config = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
    }

    provider = NlpEngineProvider(nlp_configuration=nlp_config)
    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])

    # Entity mapping for GLiNER
    entity_mapping = {
        "person": "PERSON",
        "name": "PERSON",
        "organization": "ORGANIZATION",
        "location": "LOCATION",
        "phone number": "PHONE_NUMBER",
        "email": "EMAIL_ADDRESS",
        "email address": "EMAIL_ADDRESS",
        "credit card number": "CREDIT_CARD",
        "social security number": "US_SSN",
        "date of birth": "DATE_TIME",
        "address": "LOCATION",
    }

    # Create GLiNER recognizer - will auto-detect GPU via DeviceDetector
    gliner_recognizer = GLiNERRecognizer(
        model_name="urchade/gliner_multi_pii-v1",
        entity_mapping=entity_mapping,
        flat_ner=False,
        multi_label=True,
    )

    # Add GLiNER and remove spaCy NER recognizer
    analyzer.registry.add_recognizer(gliner_recognizer)
    analyzer.registry.remove_recognizer("SpacyRecognizer")

    return analyzer


def create_stanza_analyzer():
    """Create an analyzer with Stanza NLP engine."""
    if not HAS_STANZA:
        raise ImportError(
            "Stanza support not available. "
            "Install with: pip install 'presidio-analyzer[stanza]'"
        )

    # Entity mapping from stanza.yaml config
    mapping = {
        "PER": "PERSON",
        "PERSON": "PERSON",
        "NORP": "NRP",
        "FAC": "LOCATION",
        "LOC": "LOCATION",
        "LOCATION": "LOCATION",
        "GPE": "LOCATION",
        "ORG": "ORGANIZATION",
        "ORGANIZATION": "ORGANIZATION",
        "DATE": "DATE_TIME",
        "TIME": "DATE_TIME",
    }

    ner_model_configuration = NerModelConfiguration(
        model_to_presidio_entity_mapping=mapping,
        labels_to_ignore=["O"]
    )

    # Create Stanza NLP engine with GPU support
    nlp_engine = StanzaNlpEngine(
        models=[{"lang_code": "en", "model_name": "en"}],
        ner_model_configuration=ner_model_configuration
    )

    return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])


def run_benchmark(num_texts, batch_size, engine_type="spacy"):
    """Run benchmark for a specific dataset size and NLP engine.

    Args:
        num_texts: Number of texts to process
        batch_size: Batch size for processing
        engine_type: Type of NLP engine - "spacy", "transformers", or "gliner"
    """
    print(f"\n{'='*80}")
    print(
        f"Running benchmark: {num_texts} texts, "
        f"batch_size={batch_size}, engine={engine_type}"
    )
    print('='*80)

    # Generate texts
    print(f"Generating {num_texts} test texts...")
    texts = generate_test_texts(num_texts)

    # Initialize analyzer based on engine type
    print(f"Initializing AnalyzerEngine ({engine_type})...")
    start_init = time.time()

    if engine_type == "transformers":
        analyzer = create_transformers_analyzer()
    elif engine_type == "gliner":
        analyzer = create_gliner_analyzer()
    elif engine_type == "stanza":
        analyzer = create_stanza_analyzer()
    else:  # spacy (default)
        analyzer = AnalyzerEngine()

    batch_analyzer = BatchAnalyzerEngine(analyzer)
    init_time = time.time() - start_init
    print(f"  Initialization: {init_time:.2f}s")

    # Warm-up
    print("Warm-up run...")
    start_warmup = time.time()
    _ = batch_analyzer.analyze_iterator(
        texts=texts[:min(10, num_texts)],
        language="en",
        batch_size=batch_size,
    )
    warmup_time = time.time() - start_warmup
    print(f"  Warm-up: {warmup_time:.2f}s")

    # Main benchmark
    print(f"Processing {num_texts} texts...")
    start_analysis = time.time()
    results = batch_analyzer.analyze_iterator(
        texts=texts,
        language="en",
        batch_size=batch_size,
    )
    total_analysis_time = time.time() - start_analysis

    total_entities = sum(len(result) for result in results)
    avg_time = total_analysis_time / num_texts
    throughput = num_texts / total_analysis_time

    print(f"  Complete: {total_analysis_time:.2f}s")
    print(f"  Throughput: {throughput:.2f} texts/second")
    print(f"  Entities found: {total_entities}")

    return {
        "num_texts": num_texts,
        "batch_size": batch_size,
        "engine_type": engine_type,
        "init_time": init_time,
        "warmup_time": warmup_time,
        "total_time": total_analysis_time,
        "avg_time_ms": avg_time * 1000,
        "throughput": throughput,
        "total_entities": total_entities,
    }


def main():
    """Run comprehensive benchmarks on Presidio Analyzer engines."""
    parser = argparse.ArgumentParser(
        description="Comprehensive Presidio Analyzer performance benchmark"
    )
    parser.add_argument(
        "--json",
        type=str,
        default="benchmark_results.json",
        help="Save results as JSON to this file (default: benchmark_results.json)",
    )
    parser.add_argument(
        "--engines",
        type=str,
        default="spacy",
        help=(
            "Comma-separated list of engines to test: "
            "spacy,transformers,gliner,stanza (default: spacy)"
        ),
    )
    parser.add_argument(
        "--sizes",
        type=str,
        default="50,500,5000",
        help="Comma-separated list of dataset sizes to test (default: 50,500,5000)",
    )
    args = parser.parse_args()

    # Parse engines to test
    requested_engines = [e.strip() for e in args.engines.split(',')]
    available_engines = []

    for engine in requested_engines:
        if engine == "spacy":
            available_engines.append("spacy")
        elif engine == "transformers":
            if HAS_TRANSFORMERS:
                available_engines.append("transformers")
            else:
                print(
                    "⚠️  Transformers engine requested but not available. "
                    "Install with: pip install 'presidio-analyzer[transformers]'"
                )
        elif engine == "gliner":
            if HAS_GLINER:
                available_engines.append("gliner")
            else:
                print(
                    "⚠️  GLiNER engine requested but not available. "
                    "Install with: pip install 'presidio-analyzer[gliner]'"
                )
        elif engine == "stanza":
            if HAS_STANZA:
                available_engines.append("stanza")
            else:
                print(
                    "⚠️  Stanza engine requested but not available. "
                    "Install with: pip install 'presidio-analyzer[stanza]'"
                )
        else:
            print(f"⚠️  Unknown engine: {engine}. Skipping.")

    if not available_engines:
        print("❌ No valid engines available. Exiting.")
        sys.exit(1)

    # Parse dataset sizes
    try:
        dataset_sizes = [int(s.strip()) for s in args.sizes.split(',')]
    except ValueError:
        print(
            "❌ Invalid dataset sizes format. "
            "Use comma-separated integers (e.g., 50,500,5000)"
        )
        sys.exit(1)

    # Auto-adjust batch sizes based on dataset size
    def get_batch_size(num_texts):
        return 16

    # Create test configurations
    test_configs = []
    for engine in available_engines:
        for size in dataset_sizes:
            batch_size = get_batch_size(size)
            test_configs.append((size, batch_size, engine))

    print("="*80)
    print("PRESIDIO ANALYZER COMPREHENSIVE BENCHMARK")
    print("="*80)
    print(f"\nEngines to test: {', '.join(available_engines)}")
    print(f"Dataset sizes: {', '.join(str(s) for s in dataset_sizes)}")
    print(f"Total tests: {len(test_configs)}")
    print("This may take several minutes...\n")

    all_results = []

    for num_texts, batch_size, engine in test_configs:
        try:
            result = run_benchmark(num_texts, batch_size, engine)
            all_results.append(result)
        except KeyboardInterrupt:
            print("\n\n⚠️  Benchmark interrupted by user")
            if all_results:
                print("Generating partial results...")
            else:
                print("No results to save.")
                sys.exit(1)
            break
        except Exception as e:
            print(
                f"\n❌ Error running benchmark for {num_texts} texts "
                f"with {engine} engine: {e}"
            )
            import traceback
            traceback.print_exc()
            continue

    if all_results:
        # Save JSON results
        with open(args.json, 'w') as f:
            json.dump(all_results, f, indent=2)
        print(f"✅ JSON results saved to: {args.json}")

        print("\n" + "="*80)
        print("BENCHMARK COMPLETE")
        print("="*80)
    else:
        print("\n❌ No results collected")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
