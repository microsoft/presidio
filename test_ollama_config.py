#!/usr/bin/env python3
"""
Test script to verify Ollama recognizer can be loaded from YAML configuration.

This script tests whether enabling OllamaLangExtractRecognizer in the
default_recognizers.yaml actually works correctly.
"""

import os
import sys
from pathlib import Path

# Add presidio-analyzer to path
analyzer_path = Path(__file__).parent / "presidio-analyzer"
sys.path.insert(0, str(analyzer_path))

print("=" * 80)
print("Testing Ollama Recognizer Configuration Loading")
print("=" * 80)

# Test 1: Load configuration with Ollama enabled (default)
print("\n[TEST 1] Loading default configuration (Ollama enabled)...")
try:
    from presidio_analyzer.recognizer_registry import RecognizerRegistryProvider

    default_config_path = (
        analyzer_path / "presidio_analyzer" / "conf" / "default_recognizers.yaml"
    )
    print(f"Config file: {default_config_path}")

    provider = RecognizerRegistryProvider(conf_file=str(default_config_path))
    registry = provider.create_recognizer_registry()

    # Check if Ollama recognizer is in the registry
    ollama_recognizers = [r for r in registry.recognizers if "Ollama" in r.name]

    print("✓ Configuration loaded successfully")
    print(f"  Total recognizers: {len(registry.recognizers)}")
    print(f"  Ollama recognizers: {len(ollama_recognizers)}")

    if not ollama_recognizers:
        print("  ✗ FAILED: Ollama recognizer NOT found but should be enabled!")
        sys.exit(1)
    else:
        print("  ✓ Ollama recognizer correctly loaded (enabled)")
        for rec in ollama_recognizers:
            print(f"    - Name: {rec.name}")
            print(f"      Language: {rec.supported_language}")
            print(f"      Entities: {rec.supported_entities}")

except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Try to use the Ollama recognizer (requires Ollama service)
print("\n[TEST 2] Testing Ollama recognizer functionality...")
print("NOTE: This test requires Ollama service to be running")

try:
    # Check if Ollama is available
    import requests
    ollama_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
    print(f"  Checking Ollama at: {ollama_url}")

    try:
        response = requests.get(f"{ollama_url}/api/tags", timeout=2)
        ollama_available = response.status_code == 200
    except Exception:
        ollama_available = False

    if not ollama_available:
        print("  ⚠️  Ollama service not available - skipping functional test")
        print("     To test functionality, start Ollama service and run again")
    else:
        print("  ✓ Ollama service is available")

        # Try to analyze text with the Ollama recognizer
        from presidio_analyzer import AnalyzerEngine

        analyzer = AnalyzerEngine(registry=registry, supported_languages=["en"])

        test_text = "My name is John Smith and my email is john@example.com"
        print(f"  Test text: {test_text}")

        results = analyzer.analyze(test_text, language="en")

        print("  ✓ Analysis completed")
        print(f"    Results found: {len(results)}")

        if results:
            for result in results:
                text_snippet = test_text[result.start : result.end]
                print(
                    f"      - {result.entity_type}: '{text_snippet}' "
                    f"(score: {result.score:.2f})"
                )
                if result.recognition_metadata:
                    recognizer_name = result.recognition_metadata.get(
                        "recognizer_name", "unknown"
                    )
                    print(f"        Detected by: {recognizer_name}")

        # Check if Ollama was used
        ollama_used = any(
            r.recognition_metadata and
            "Ollama" in r.recognition_metadata.get("recognizer_name", "")
            for r in results
        )

        if ollama_used:
            print("  ✓ Ollama recognizer successfully detected entities")
        else:
            print("  ⚠️  Ollama recognizer did not detect any entities")
            print("     (Other recognizers may have detected them first)")

except ImportError as e:
    print(f"  ⚠️  Skipping functional test - missing dependency: {e}")
except Exception as e:
    print(f"  ✗ Functional test failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print("✓ Configuration loading test completed")
print("\nNext steps:")
print("1. If Test 1 failed, check that Ollama is enabled in default_recognizers.yaml")
print("2. If Test 2 was skipped, start Ollama service to test full functionality")
print("3. Verify the config_path resolves correctly from repository root")
print("=" * 80)
