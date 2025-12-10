#!/usr/bin/env python3
"""Test script to benchmark Presidio Analyzer with BATCH processing and GPU detection."""

import argparse
import os
import time
import sys
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.batch_analyzer_engine import BatchAnalyzerEngine
from presidio_analyzer.nlp_engine import DeviceDetector

# Sample texts for testing - large dataset
TEST_TEXTS = []

# Generate varied texts with PII
base_texts = [
    "My name is {name} and my email is {email}. I work at {company} as a software engineer.",
    "Patient information: Name: {name}, SSN: {ssn}, Phone: {phone}, Address: {address}",
    "Dear {name}, your account {email} has been verified. Contact us at {phone} for support.",
    "Employee ID: {id}, Name: {name}, Credit Card: {cc}, Expires: {exp_date}",
    "Contact {name} at {phone} or email {email}. Office located at {address}.",
    "Medical record for {name}, born {dob}. Insurance details: Policy #{id}, contact {phone}.",
    "Transaction approved for {name}. Card ending {cc_last4}. Receipt sent to {email}.",
    "Hello {name}, your appointment at {address} is confirmed for {date} at {time}. Call {phone} if needed.",
    "User profile: {name}, Username: {email}, Phone: {phone}, Registered: {date}",
    "Billing statement for {name} at {address}. Amount due: $2,500. Questions? Email {email} or call {phone}.",
    "Dear Dr. {name}, patient consultation scheduled {date}. Patient contact: {phone}, Address: {address}",
    "Account #{id} for {name} ({email}) shows activity on {date}. Security code sent to {phone}.",
    "Prescription refill for {name}, DOB: {dob}. Pharmacy: {address}. Insurance verification needed, call {phone}.",
    "Welcome {name}! Your credit card {cc} has been added. Billing address: {address}. Contact: {email}",
    "Invoice #{id} - {name}, {company}. Payment to {address}. Due {date}. Support: {email}/{phone}",
]

names = [
    "John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "James Wilson",
    "Jessica Martinez", "David Anderson", "Jennifer Taylor", "Robert Thomas", "Mary Garcia",
    "Christopher Lee", "Patricia Rodriguez", "Daniel White", "Linda Harris", "Matthew Clark",
    "Barbara Lewis", "Joseph Walker", "Susan Hall", "Charles Allen", "Karen Young"
]

emails = [
    "john.smith@example.com", "sarah.j@company.org", "mbrown@corp.net", "emily.davis@mail.com",
    "jwilson@business.io", "jmartinez@enterprise.com", "david.a@startup.tech", "jtaylor@firm.law",
    "rthomas@clinic.med", "mgarcia@university.edu", "clee@consulting.biz", "prodriguez@agency.gov",
    "dwhite@financial.com", "lharris@retail.store", "mclark@manufacturing.ind", "blewis@services.pro",
    "jwalker@healthcare.org", "shall@education.edu", "callen@technology.io", "kyoung@pharma.com"
]

phones = [
    "555-123-4567", "555-234-5678", "555-345-6789", "555-456-7890", "555-567-8901",
    "+1-555-678-9012", "+1-202-555-0173", "555-789-0123", "555-890-1234", "555-901-2345",
    "+1-415-555-0198", "+1-310-555-0142", "555-111-2222", "555-222-3333", "555-333-4444",
    "+1-713-555-0156", "+1-617-555-0187", "555-444-5555", "555-555-6666", "555-666-7777"
]

ssns = [
    "123-45-6789", "234-56-7890", "345-67-8901", "456-78-9012", "567-89-0123",
    "678-90-1234", "789-01-2345", "890-12-3456", "901-23-4567", "012-34-5678",
    "111-22-3333", "222-33-4444", "333-44-5555", "444-55-6666", "555-66-7777",
    "666-77-8888", "777-88-9999", "888-99-0000", "999-00-1111", "000-11-2222"
]

addresses = [
    "123 Main St, New York, NY 10001", "456 Oak Ave, Los Angeles, CA 90012",
    "789 Pine Rd, Chicago, IL 60601", "321 Elm St, Houston, TX 77001",
    "654 Maple Dr, Phoenix, AZ 85001", "987 Cedar Ln, Philadelphia, PA 19101",
    "147 Birch Way, San Antonio, TX 78201", "258 Spruce Ct, San Diego, CA 92101",
    "369 Willow Pl, Dallas, TX 75201", "741 Ash Blvd, San Jose, CA 95101",
    "852 Hickory St, Austin, TX 78701", "963 Walnut Ave, Jacksonville, FL 32099",
    "159 Chestnut Rd, Fort Worth, TX 76101", "357 Magnolia Dr, Columbus, OH 43004",
    "486 Sycamore Ln, Charlotte, NC 28201"
]

credit_cards = [
    "4532-1234-5678-9010", "5425-2345-6789-0123", "3782-345678-90123",
    "6011-4567-8901-2345", "3056-567890-1234", "4916-6789-0123-4567",
    "5412-7890-1234-5678", "3714-890123-45678", "6011-9012-3456-7890"
]

dates = [
    "01/15/2024", "02/20/2024", "03/25/2024", "04/10/2024", "05/18/2024",
    "06/22/2024", "07/30/2024", "08/14/2024", "09/05/2024", "10/12/2024",
    "11/28/2024", "12/31/2024"
]

times = ["10:30 AM", "2:15 PM", "9:00 AM", "4:45 PM", "11:20 AM", "3:30 PM", "8:15 AM"]
dobs = ["05/15/1985", "08/22/1990", "03/10/1978", "11/05/1982", "07/30/1995", "12/18/1988"]

# Generate 50000 test texts for large-scale GPU testing
for i in range(50000):
    template = base_texts[i % len(base_texts)]
    text = template.format(
        name=names[i % len(names)],
        email=emails[i % len(emails)],
        phone=phones[i % len(phones)],
        ssn=ssns[i % len(ssns)],
        address=addresses[i % len(addresses)],
        company=f"Company{i % 50}",
        id=f"EMP{10000 + i}",
        cc=credit_cards[i % len(credit_cards)],
        cc_last4=str(1000 + i % 9000),
        exp_date=dates[i % len(dates)],
        date=dates[i % len(dates)],
        time=times[i % len(times)],
        dob=dobs[i % len(dobs)],
    )
    TEST_TEXTS.append(text)


def run_benchmark(force_cpu=False, batch_size=32):
    """Run the benchmark test with batch processing."""
    device_mode = "CPU-ONLY MODE" if force_cpu else "AUTO-DETECT MODE"
    
    print("=" * 80)
    print(f"Presidio BATCH Performance Test ({device_mode})")
    print(f"Texts: {len(TEST_TEXTS)}, Batch Size: {batch_size}")
    print("=" * 80)
    
    # Force CPU mode if requested
    if force_cpu:
        print("\n[!] Forcing CPU mode (disabling CUDA)...")
        os.environ["CUDA_VISIBLE_DEVICES"] = ""
    
    # Check device detection
    print("\n[1] Device Detection:")
    device_detector = DeviceDetector()
    device_info = device_detector.get_torch_device_info()
    print(f"  - Has GPU: {device_info['has_gpu']}")
    print(f"  - Device: {device_info['device']}")
    print(f"  - Device Name: {device_info['device_name']}")
    
    # Initialize analyzer
    print("\n[2] Initializing AnalyzerEngine...")
    start_init = time.time()
    analyzer = AnalyzerEngine()
    batch_analyzer = BatchAnalyzerEngine(analyzer)
    init_time = time.time() - start_init
    print(f"  - Initialization time: {init_time:.2f} seconds")
    
    # Warm-up run
    print("\n[3] Warm-up run...")
    start_warmup = time.time()
    _ = batch_analyzer.analyze_iterator(
        texts=TEST_TEXTS[:10],
        language="en",
        batch_size=batch_size,
    )
    warmup_time = time.time() - start_warmup
    print(f"  - Warm-up time: {warmup_time:.2f} seconds")
    
    # Batch performance test
    print(f"\n[4] Batch processing {len(TEST_TEXTS)} texts (batch_size={batch_size})...")
    start_analysis = time.time()
    
    results = batch_analyzer.analyze_iterator(
        texts=TEST_TEXTS,
        language="en",
        batch_size=batch_size,
    )
    
    total_analysis_time = time.time() - start_analysis
    total_entities = sum(len(result) for result in results)
    avg_time = total_analysis_time / len(TEST_TEXTS)
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    print(f"Device: {device_info['device']} ({device_info['device_name'] or 'CPU'})")
    print(f"Texts processed: {len(TEST_TEXTS)}")
    print(f"Batch size: {batch_size}")
    print(f"Initialization time: {init_time:.2f}s")
    print(f"Warm-up time: {warmup_time:.2f}s")
    print(f"Total analysis time: {total_analysis_time:.3f}s")
    print(f"Average time per text: {avg_time:.4f}s")
    print(f"Total entities found: {total_entities}")
    print(f"Throughput: {len(TEST_TEXTS) / total_analysis_time:.2f} texts/second")
    print("=" * 80)
    
    return {
        "device": device_info['device'],
        "device_name": device_info['device_name'] or 'CPU',
        "has_gpu": device_info['has_gpu'],
        "num_texts": len(TEST_TEXTS),
        "batch_size": batch_size,
        "init_time": init_time,
        "warmup_time": warmup_time,
        "total_time": total_analysis_time,
        "avg_time": avg_time,
        "throughput": len(TEST_TEXTS) / total_analysis_time,
        "total_entities": total_entities,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Presidio Analyzer BATCH processing with GPU"
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU mode (disable GPU)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Batch size for processing (default: 32)",
    )
    args = parser.parse_args()
    
    results = run_benchmark(force_cpu=args.cpu, batch_size=args.batch_size)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
