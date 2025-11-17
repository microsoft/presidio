#!/usr/bin/env python
"""Profiler for Presidio Analyzer - Run with: poetry run python profile_analyzer.py"""

import cProfile
import subprocess
from pathlib import Path
from presidio_analyzer import AnalyzerEngine


def run_analyzer_workload():
    """Run analyzer on sample texts."""
    print("Initializing AnalyzerEngine...")
    analyzer = AnalyzerEngine()
    
    texts = [
        "John Smith's credit card is 4095-2609-9393-4932 and phone is 425-882-9090",
        "Email: john.doe@example.com, Address: 123 Main St, New York, NY 10001",
        "SSN: 078-05-1120, DOB: 01/01/1990, IP: 192.168.1.1",
    ] * 20  # 60 samples total
    
    print(f"Analyzing {len(texts)} samples...")
    for text in texts:
        analyzer.analyze(text=text, language="en")
    print(f"✓ Complete")


def generate_svg(profiler_file: Path):
    """Generate SVG call graph visualization."""
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    svg_file = output_dir / "profiler.svg"
    
    try:
        print("\nGenerating SVG...")
        cmd = f"gprof2dot -f pstats {profiler_file} -n 0.02 -e 0.02 | dot -Tsvg -o {svg_file}"
        subprocess.run(cmd, shell=True, check=True, capture_output=True)
        print(f"✓ Created {svg_file} (red=hottest, yellow-green=hot, blue=coolest)")
    except subprocess.CalledProcessError:
        print("⚠️  Install: poetry add --group dev gprof2dot && sudo apt install graphviz")
    except FileNotFoundError:
        print("⚠️  Install: poetry add --group dev gprof2dot && sudo apt install graphviz")


if __name__ == "__main__":
    print("Presidio Analyzer Profiler")
    print("-" * 50)
    
    # Set up output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    profiler_out = output_dir / "profiler.out"
    
    # Profile the workload
    cProfile.run('run_analyzer_workload()', str(profiler_out), sort='cumtime')
    
    # Show top 15 functions
    print(f"\n{'Top 15 Functions by Time':-^50}")
    subprocess.run(f'python -m pstats {profiler_out} <<EOF\nsort cumtime\nstats 15\nquit\nEOF', 
                   shell=True, executable='/bin/bash')
    
    # Generate SVG
    generate_svg(profiler_out)
    
    print(f"\n{'Done':-^50}")
    print(f"Output: profiler/output/profiler.{{out,svg}}")
    print(f"View stats: python -m pstats {profiler_out}")
