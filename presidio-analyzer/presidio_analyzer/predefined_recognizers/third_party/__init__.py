"""Third-party recognizers package."""

from .azure_ai_language import AzureAILanguageRecognizer
from .ahds_recognizer import AzureHealthDeidRecognizer

__all__ = [
    "AzureAILanguageRecognizer",
    "AzureHealthDeidRecognizer"
]
