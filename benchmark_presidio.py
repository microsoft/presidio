#!/usr/bin/env python3
"""
Comprehensive benchmark script for Presidio Analyzer performance testing.
Tests different dataset sizes and generates a markdown report.
"""

import argparse
import json
import time
import sys
from datetime import datetime
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.batch_analyzer_engine import BatchAnalyzerEngine
from presidio_analyzer.nlp_engine import DeviceDetector

# Sample texts for testing - large dataset
TEST_TEXT_TEMPLATES = [
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

NAMES = [
    "John Smith", "Sarah Johnson", "Michael Brown", "Emily Davis", "James Wilson",
    "Jessica Martinez", "David Anderson", "Jennifer Taylor", "Robert Thomas", "Mary Garcia",
    "Christopher Lee", "Patricia Rodriguez", "Daniel White", "Linda Harris", "Matthew Clark",
    "Barbara Lewis", "Joseph Walker", "Susan Hall", "Charles Allen", "Karen Young"
]

EMAILS = [
    "john.smith@example.com", "sarah.j@company.org", "mbrown@corp.net", "emily.davis@mail.com",
    "jwilson@business.io", "jmartinez@enterprise.com", "david.a@startup.tech", "jtaylor@firm.law",
    "rthomas@clinic.med", "mgarcia@university.edu", "clee@consulting.biz", "prodriguez@agency.gov",
    "dwhite@financial.com", "lharris@retail.store", "mclark@manufacturing.ind", "blewis@services.pro",
    "jwalker@healthcare.org", "shall@education.edu", "callen@technology.io", "kyoung@pharma.com"
]

PHONES = [
    "555-123-4567", "555-234-5678", "555-345-6789", "555-456-7890", "555-567-8901",
    "+1-555-678-9012", "+1-202-555-0173", "555-789-0123", "555-890-1234", "555-901-2345",
    "+1-415-555-0198", "+1-310-555-0142", "555-111-2222", "555-222-3333", "555-333-4444",
    "+1-713-555-0156", "+1-617-555-0187", "555-444-5555", "555-555-6666", "555-666-7777"
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

TIMES = ["10:30 AM", "2:15 PM", "9:00 AM", "4:45 PM", "11:20 AM", "3:30 PM", "8:15 AM"]
DOBS = ["05/15/1985", "08/22/1990", "03/10/1978", "11/05/1982", "07/30/1995", "12/18/1988"]


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


def run_benchmark(num_texts, batch_size):
    """Run benchmark for a specific dataset size."""
    print(f"\n{'='*80}")
    print(f"Running benchmark: {num_texts} texts, batch_size={batch_size}")
    print('='*80)
    
    # Generate texts
    print(f"Generating {num_texts} test texts...")
    texts = generate_test_texts(num_texts)
    
    # Get device info
    device_detector = DeviceDetector()
    device_info = device_detector.get_torch_device_info()
    
    print(f"Device: {device_info['device']} ({device_info['device_name'] or 'CPU'})")
    
    # Initialize analyzer
    print("Initializing AnalyzerEngine...")
    start_init = time.time()
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
        "device": device_info['device'],
        "device_name": device_info['device_name'] or 'CPU',
        "has_gpu": device_info['has_gpu'],
        "init_time": init_time,
        "warmup_time": warmup_time,
        "total_time": total_analysis_time,
        "avg_time_ms": avg_time * 1000,
        "throughput": throughput,
        "total_entities": total_entities,
    }


def generate_markdown_report(results, output_file):
    """Generate a markdown report from benchmark results."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Get device info from first result
    device_name = results[0]['device_name']
    device = results[0]['device']
    has_gpu = results[0]['has_gpu']
    
    md = f"""# Presidio Analyzer Performance Benchmark

**Date**: {timestamp}  
**Device**: {device} ({device_name})  
**GPU Enabled**: {has_gpu}

## Summary

This benchmark measures Presidio Analyzer performance across different dataset sizes using batch processing.

## Results

| Dataset Size | Batch Size | Total Time (s) | Avg Time (ms) | Throughput (texts/s) | Entities Found |
|--------------|------------|----------------|---------------|---------------------|----------------|
"""
    
    for result in results:
        md += f"| {result['num_texts']:,} | {result['batch_size']} | {result['total_time']:.2f} | {result['avg_time_ms']:.2f} | {result['throughput']:.2f} | {result['total_entities']:,} |\n"
    
    md += f"""
## Performance Scaling

"""
    
    # Calculate scaling metrics
    base_result = results[0]
    base_throughput = base_result['throughput']
    
    md += "| Dataset Size | Throughput (texts/s) | Scaling Factor | Efficiency |\n"
    md += "|--------------|---------------------|----------------|------------|\n"
    
    for result in results:
        scaling_factor = result['num_texts'] / base_result['num_texts']
        efficiency = (result['throughput'] / base_throughput) / scaling_factor * 100
        md += f"| {result['num_texts']:,} | {result['throughput']:.2f} | {scaling_factor:.1f}x | {efficiency:.1f}% |\n"
    
    md += f"""
## Configuration Details

- **Initialization Time**: {results[0]['init_time']:.2f}s
- **Language**: English (en)
- **NLP Engine**: spaCy
- **Processing Mode**: Batch processing with `BatchAnalyzerEngine`

## Test Data

- Generated synthetic PII data (names, emails, phones, SSNs, addresses, credit cards, etc.)
- {len(TEST_TEXT_TEMPLATES)} unique text templates
- Varied entity types per text

## Notes

- All tests use the same spaCy NLP engine configuration
- Batch processing leverages GPU parallelization when available
- Throughput measured as texts processed per second
- Warm-up run performed before each test to ensure fair comparison

---
*Generated by Presidio Performance Benchmark Script*
"""
    
    with open(output_file, 'w') as f:
        f.write(md)
    
    print(f"\n✅ Markdown report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Presidio Analyzer performance benchmark"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.md",
        help="Output markdown file (default: benchmark_results.md)",
    )
    parser.add_argument(
        "--json",
        type=str,
        help="Also save results as JSON to this file",
    )
    args = parser.parse_args()
    
    # Test configurations: (num_texts, batch_size)
    test_configs = [
        (50, 16),
        (500, 32),
        (5000, 64),
        (50000, 128),
    ]
    
    print("="*80)
    print("PRESIDIO ANALYZER COMPREHENSIVE BENCHMARK")
    print("="*80)
    print(f"\nRunning {len(test_configs)} benchmark tests...")
    print("This may take several minutes...\n")
    
    all_results = []
    
    for num_texts, batch_size in test_configs:
        try:
            result = run_benchmark(num_texts, batch_size)
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
            print(f"\n❌ Error running benchmark for {num_texts} texts: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if all_results:
        # Generate markdown report
        generate_markdown_report(all_results, args.output)
        
        # Save JSON if requested
        if args.json:
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
