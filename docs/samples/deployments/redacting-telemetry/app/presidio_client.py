"""
Presidio HTTP Client for PII Masking
"""

import os
import requests
from typing import List, Dict


# Configuration
ANALYZER_URL = os.getenv("PRESIDIO_ANALYZER_URL", "http://presidio-analyzer:3000")
ANONYMIZER_URL = os.getenv("PRESIDIO_ANONYMIZER_URL", "http://presidio-anonymizer:3000")


def analyze_text(text: str, language: str = "en") -> List[Dict]:
    """Analyze text for PII entities using Presidio Analyzer."""
    payload = {
        "text": text,
        "language": language
    }
    
    try:
        response = requests.post(
            f"{ANALYZER_URL}/analyze",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error calling Presidio Analyzer: {e}")
        return []


def anonymize_text(text: str, analyzer_results: List[Dict]) -> str:
    """Anonymize text based on analyzer results."""
    if not analyzer_results:
        return text
    
    payload = {
        "text": text,
        "analyzer_results": analyzer_results
    }
    
    try:
        response = requests.post(
            f"{ANONYMIZER_URL}/anonymize",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        return result.get("text", text)
    except Exception as e:
        print(f"Error calling Presidio Anonymizer: {e}")
        return text


def mask_pii(text: str, language: str = "en") -> str:
    """One-step function to mask PII in text."""
    if not text or not text.strip():
        return text
    
    # Analyze for PII
    analyzer_results = analyze_text(text, language=language)
    
    if not analyzer_results:
        return text
    
    # Anonymize
    return anonymize_text(text, analyzer_results)
