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
        result = subprocess.run(
            "curl -fsSL https://ollama.com/install.sh | sh",
            shell=True,
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    elif system == "Darwin":
        print("Installing Ollama on macOS...")
        result = subprocess.run(["brew", "install", "ollama"], capture_output=True)
        return result.returncode == 0
    else:
        print("Windows: Please download from https://ollama.com/download")
        return False

def start_ollama():
    """Start Ollama service in background."""
    subprocess.Popen(
        ["ollama", "serve"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(5)

def check_ollama(retries=10):
    """Check if Ollama is responding."""
    for _ in range(retries):
        try:
            with urllib.request.urlopen(f"{OLLAMA_URL}/api/tags", timeout=2) as response:
                if response.status == 200:
                    return True
        except:
            time.sleep(2)
    return False

def main():
    print("Ollama Setup")
    print("="*40)
    
    # Check if ollama command exists
    try:
        subprocess.run(["ollama", "--version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.SubprocessError):
        if not install_ollama():
            print("✗ Installation failed")
            sys.exit(1)
        print("✓ Installed")
    
    # Check if running
    if not check_ollama(retries=1):
        start_ollama()
        if not check_ollama():
            print("✗ Failed to start")
            sys.exit(1)
    
    print("✓ Ollama ready")

if __name__ == "__main__":
    main()
