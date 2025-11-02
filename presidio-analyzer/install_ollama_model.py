#!/usr/bin/env python3
"""
Install and setup Ollama with required model for LangExtract.
Cross-platform script for Linux, macOS, and Windows.
"""
import platform
import subprocess
import sys
import time
import urllib.request

OLLAMA_URL = "http://localhost:11434"

def install_ollama():
    """Install Ollama based on operating system."""
    system = platform.system()

    if system == "Linux":
        print("Installing Ollama on Linux...")
        print("This may take a few minutes. Please wait...")
        result = subprocess.run(
            "curl -fsSL https://ollama.com/install.sh | sh",
            shell=True,
            text=True
        )
        if result.returncode == 0:
            print("✓ Installation completed")
        else:
            print("✗ Installation failed")
        return result.returncode == 0
    elif system == "Darwin":
        print("Installing Ollama on macOS...")
        print("This may take a few minutes. Please wait...")
        result = subprocess.run(["brew", "install", "ollama"])
        if result.returncode == 0:
            print("✓ Installation completed")
        else:
            print("✗ Installation failed")
        return result.returncode == 0
    else:
        print("Windows: Please download from https://ollama.com/download")
        return False

def start_ollama():
    """Start Ollama service in background."""
    print("Starting Ollama service...")
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    print("Waiting for service to start...")
    time.sleep(5)
    print("✓ Service started")

def check_ollama(retries=10):
    """Check if Ollama is responding."""
    print("Checking Ollama connectivity...")
    for i in range(retries):
        try:
            with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as response:
                if response.status == 200:
                    return True
        except:
            if i < retries - 1:
                print(f"  Retry {i+1}/{retries}...")
            time.sleep(2)
    return False

def main():
    print("Ollama Setup")
    print("="*40)

    # Check if ollama command exists
    print("Checking for Ollama installation...")
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
        print("✓ Ollama already installed")
    except (FileNotFoundError, subprocess.SubprocessError):
        if not install_ollama():
            print("✗ Installation failed")
            sys.exit(1)

    # Check if running
    if not check_ollama(retries=1):
        start_ollama()
        if not check_ollama():
            print("✗ Failed to start")
            sys.exit(1)
    else:
        print("✓ Ollama already running")

    print("\n" + "="*40)
    print("✓ Ollama ready")
    print("="*40)

if __name__ == "__main__":
    main()
