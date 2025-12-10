#!/usr/bin/env python3
"""Test script to benchmark Presidio Analyzer with GPU detection."""

import argparse
import os
import time
import sys
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import DeviceDetector

# Sample texts for testing - large dataset
TEST_TEXTS = []

# Generate 100 varied texts with PII
base_texts = [
    "My name is {name} and my email is {email}. I work at {company} as a software engineer.",
    "Patient information: Name: {name}, SSN: {ssn}, Phone: {phone}, Address: {address}",
    "Dear {name}, your account {email} has been verified. Contact us at {phone} for support.",
    "Employee ID: {id}, Name: {name}, Credit Card: {cc}, Expires: {exp_date}",
    "Contact {name} at {phone} or email {email}. Office located at {address}.",
    "Dr. {name} will see you on {date} at {time}. Please bring your insurance card and ID to {address}.",
    "Invoice for {name}: Total $5,000. Payment due {date}. Card ending in {cc_last4}. Email confirmation sent to {email}.",
    "Prescription for {name}, DOB: {dob}, Address: {address}. Fill at pharmacy, call {phone} with questions.",
    "Welcome {name}! Your username is {email} and temporary password was sent to {phone}. Login at https://portal.example.com.",
    "Claim #{id} for {name} approved. Check mailed to {address}. Questions? Call {phone} Mon-Fri 9-5 EST.",
]

names = ["John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "James Wilson", 
         "Jessica Martinez", "David Anderson", "Jennifer Taylor", "Robert Thomas", "Mary Garcia"]
emails = ["john.smith@example.com", "sarah.j@company.org", "mbrown@corp.net", "emily.davis@mail.com",
          "jwilson@business.io", "jmartinez@enterprise.com", "david.a@startup.tech", "jtaylor@firm.law",
          "rthomas@clinic.med", "mgarcia@university.edu"]
phones = ["555-123-4567", "555-234-5678", "555-345-6789", "555-456-7890", "555-567-8901",
          "+1-555-678-9012", "+1-202-555-0173", "555-789-0123", "555-890-1234", "555-901-2345"]
ssns = ["123-45-6789", "234-56-7890", "345-67-8901", "456-78-9012", "567-89-0123",
        "678-90-1234", "789-01-2345", "890-12-3456", "901-23-4567", "012-34-5678"]
addresses = ["123 Main St, New York, NY 10001", "456 Oak Ave, Los Angeles, CA 90012",
             "789 Pine Rd, Chicago, IL 60601", "321 Elm St, Houston, TX 77001",
             "654 Maple Dr, Phoenix, AZ 85001", "987 Cedar Ln, Philadelphia, PA 19101",
             "147 Birch Way, San Antonio, TX 78201", "258 Spruce Ct, San Diego, CA 92101",
             "369 Willow Pl, Dallas, TX 75201", "741 Ash Blvd, San Jose, CA 95101"]
credit_cards = ["4532-1234-5678-9010", "5425-2345-6789-0123", "3782-345678-90123",
                "6011-4567-8901-2345", "3056-567890-1234", "4916-6789-0123-4567"]
dates = ["01/15/2024", "02/20/2024", "03/25/2024", "12/31/2024", "06/15/2024"]
times = ["10:30 AM", "2:15 PM", "9:00 AM", "4:45 PM", "11:20 AM"]
dobs = ["05/15/1985", "08/22/1990", "03/10/1978", "11/05/1982", "07/30/1995"]

# Generate 100 test texts
for i in range(100):
    template = base_texts[i % len(base_texts)]
    text = template.format(
        name=names[i % len(names)],
        email=emails[i % len(emails)],
        phone=phones[i % len(phones)],
        ssn=ssns[i % len(ssns)],
        address=addresses[i % len(addresses)],
        company=f"Company{i % 20}",
        id=f"EMP{1000 + i}",
        cc=credit_cards[i % len(credit_cards)],
        cc_last4=str(1000 + i % 9000),
        exp_date=dates[i % len(dates)],
        date=dates[i % len(dates)],
        time=times[i % len(times)],
        dob=dobs[i % len(dobs)],
    )
    TEST_TEXTS.append(text)


def run_benchmark(force_cpu=False):
    """Run the benchmark test."""
    device_mode = "CPU-ONLY MODE" if force_cpu else "AUTO-DETECT MODE"
    
    print("=" * 80)
    print(f"Presidio Analyzer GPU Performance Test ({device_mode})")
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
    init_time = time.time() - start_init
    print(f"  - Initialization time: {init_time:.2f} seconds")
    
    # Warm-up run
    print("\n[3] Warm-up run (first analysis)...")
    start_warmup = time.time()
    _ = analyzer.analyze(text=TEST_TEXTS[0], language="en")
    warmup_time = time.time() - start_warmup
    print(f"  - Warm-up time: {warmup_time:.2f} seconds")
    
    # Performance test
    print("\n[4] Performance test (analyzing multiple texts)...")
    start_analysis = time.time()
    total_entities = 0
    
    for i, text in enumerate(TEST_TEXTS, 1):
        text_start = time.time()
        results = analyzer.analyze(text=text, language="en")
        text_time = time.time() - text_start
        total_entities += len(results)
        print(f"  - Text {i}: {len(results)} entities found in {text_time:.3f}s")
        for result in results:
            print(f"      {result.entity_type}: '{text[result.start:result.end]}' (score: {result.score:.2f})")
    
    total_analysis_time = time.time() - start_analysis
    avg_time = total_analysis_time / len(TEST_TEXTS)
    
    # Summary
    print("\n" + "=" * 80)
    print("Summary:")
    print("=" * 80)
    print(f"Device: {device_info['device']} ({device_info['device_name'] or 'CPU'})")
    print(f"Initialization time: {init_time:.2f}s")
    print(f"Warm-up time: {warmup_time:.2f}s")
    print(f"Total analysis time: {total_analysis_time:.3f}s")
    print(f"Average time per text: {avg_time:.3f}s")
    print(f"Total entities found: {total_entities}")
    print(f"Throughput: {len(TEST_TEXTS) / total_analysis_time:.2f} texts/second")
    print("=" * 80)
    
    return {
        "device": device_info['device'],
        "device_name": device_info['device_name'] or 'CPU',
        "has_gpu": device_info['has_gpu'],
        "init_time": init_time,
        "warmup_time": warmup_time,
        "total_time": total_analysis_time,
        "avg_time": avg_time,
        "throughput": len(TEST_TEXTS) / total_analysis_time,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark Presidio Analyzer GPU performance"
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Force CPU mode (disable GPU)",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run both GPU and CPU benchmarks for comparison",
    )
    args = parser.parse_args()
    
    if args.compare:
        print("\n" + "=" * 80)
        print("COMPARISON MODE: Running both GPU and CPU benchmarks")
        print("=" * 80 + "\n")
        
        # Run GPU benchmark first
        print("\n[Running GPU benchmark...]\n")
        gpu_results = run_benchmark(force_cpu=False)
        
        # Need to restart for CPU benchmark
        print("\n\n" + "!" * 80)
        print("RESTARTING FOR CPU BENCHMARK...")
        print("!" * 80 + "\n")
        
        import subprocess
        result = subprocess.run(
            [sys.executable, __file__, "--cpu"],
            capture_output=False
        )
        
        sys.exit(result.returncode)
    else:
        results = run_benchmark(force_cpu=args.cpu)


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
