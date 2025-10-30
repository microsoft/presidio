#!/usr/bin/env python3
"""
Simple standalone test for LangExtract recognizer.
Run from repository root: python simple_langextract_test.py
"""

def main():
    print("=" * 70)
    print("Simple LangExtract Recognizer Test")
    print("=" * 70)
    
    # Step 1: Check dependencies
    print("\n[1/4] Checking dependencies...")
    try:
        import langextract
        print("  ✓ langextract installed")
    except ImportError:
        print("  ✗ langextract not found")
        print("\nInstall with:")
        print("  pip install langextract")
        print("  OR")
        print("  cd presidio-analyzer && pip install -e .[langextract]")
        return 1
    
    try:
        from presidio_analyzer.predefined_recognizers.third_party import LangExtractRecognizer
        print("  ✓ LangExtractRecognizer available")
    except ImportError as e:
        print(f"  ✗ Cannot import LangExtractRecognizer: {e}")
        print("\nMake sure you're in the presidio repository and presidio-analyzer is installed:")
        print("  cd presidio-analyzer && pip install -e .")
        return 1
    
    # Step 2: Check for Ollama
    print("\n[2/4] Checking for Ollama...")
    import socket
    import subprocess
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 11434))
        sock.close()
        if result == 0:
            print("  ✓ Ollama is running on localhost:11434")
            use_ollama = True
        else:
            print("  ⚠ Ollama not detected (connection refused)")
            use_ollama = False
    except Exception as e:
        print(f"  ⚠ Could not check Ollama: {e}")
        use_ollama = False
    
    if not use_ollama:
        print("\n  Ollama not running. Installing and starting Ollama...")
        print("\n  Step 1: Installing Ollama...")
        try:
            # Install Ollama (Linux/macOS)
            result = subprocess.run(
                "curl -fsSL https://ollama.com/install.sh | sh",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print("  ✓ Ollama installed successfully")
            else:
                print(f"  ⚠ Ollama installation may have failed: {result.stderr}")
        except Exception as e:
            print(f"  ⚠ Could not install Ollama: {e}")
            print("\n  Manual installation:")
            print("    Linux/macOS: curl -fsSL https://ollama.com/install.sh | sh")
            print("    Windows: Download from https://ollama.com/download")
            return 1
        
        print("\n  Step 2: Starting Ollama server...")
        try:
            # Start Ollama in background
            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("  ✓ Ollama server started in background")
            
            # Wait for server to be ready
            import time
            print("  ⏳ Waiting for Ollama to be ready...", end="", flush=True)
            for _ in range(10):
                time.sleep(1)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                if sock.connect_ex(('localhost', 11434)) == 0:
                    sock.close()
                    print(" Ready!")
                    use_ollama = True
                    break
                sock.close()
                print(".", end="", flush=True)
            else:
                print("\n  ⚠ Ollama server did not start in time")
                return 1
                
        except Exception as e:
            print(f"\n  ✗ Failed to start Ollama: {e}")
            return 1
    
    # Check if model exists and pull if needed
    print("\n  Checking for llama3.2:3b model...")
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        if "llama3.2:3b" not in result.stdout:
            print("  ⚠ Model llama3.2:3b not found, pulling...")
            result = subprocess.run(
                ["ollama", "pull", "llama3.2:3b"],
                capture_output=False,  # Show progress
                text=True
            )
            if result.returncode == 0:
                print("  ✓ Model llama3.2:3b downloaded successfully")
            else:
                print(f"  ✗ Failed to pull model")
                return 1
        else:
            print("  ✓ Model llama3.2:3b already available")
    except Exception as e:
        print(f"  ✗ Failed to check/pull model: {e}")
        return 1
    
    # Step 3: Initialize recognizer
    print("\n[3/4] Initializing recognizer...")
    
    try:
        # Always try Ollama first (local model)
        import tempfile
        import yaml
        
        config = {
            "langextract": {
                "enabled": True,
                "model_id": "llama3.2:3b",
                "model_url": "http://localhost:11434",
                "max_char_buffer": 500,
                "batch_length": 5,
                "extraction_passes": 1,
                "max_workers": 2,
                "show_progress": False,
                "prompt_file": "langextract_prompts/default_pii_prompt.txt",
                "examples_file": "langextract_prompts/default_pii_examples.yaml",
                "entity_mappings": {
                    "person": "PERSON",
                    "email": "EMAIL_ADDRESS",
                    "phone": "PHONE_NUMBER",
                },
                "supported_entities": ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"],
                "min_score": 0.5,
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        recognizer = LangExtractRecognizer(
            config_path=config_path,
            supported_language="en"
        )
        print(f"  ✓ Using local Ollama model: {recognizer.model_id}")
        
        if not use_ollama:
            print(f"  ⚠ Ollama not running - install and start it first!")
            print(f"     Install: https://ollama.com/download")
            print(f"     Run: ollama pull llama3.2:3b && ollama serve")
        
        print(f"  ✓ Recognizer enabled: {recognizer.enabled}")
        print(f"  ✓ Supported entities: {len(recognizer.supported_entities)}")
        
    except Exception as e:
        print(f"  ✗ Failed to initialize: {e}")
        return 1
    
    # Step 4: Test with sample text
    print("\n[4/4] Testing PII detection...")
    
    test_cases = [
        "My name is John Doe",
        "Email me at john.doe@example.com",
        "Call me at 555-123-4567",
    ]
    
    for i, text in enumerate(test_cases, 1):
        print(f"\n  Test {i}: '{text}'")
        try:
            results = recognizer.analyze(text=text)
            
            if results:
                for result in results:
                    detected = text[result.start:result.end]
                    print(f"    ✓ {result.entity_type}: '{detected}' (score: {result.score:.2f})")
            else:
                print(f"    - No entities detected")
                
        except Exception as e:
            print(f"    ✗ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✓ Test completed!")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
