"""Third-party recognizers package."""

from .ahds_recognizer import AzureHealthDeidRecognizer
from .azure_ai_language import AzureAILanguageRecognizer

__all__ = [
    "AzureAILanguageRecognizer",
    "AzureHealthDeidRecognizer"
]
