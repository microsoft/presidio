import os
import sys
from analyzer.pattern import Pattern
from analyzer.recognizer_result import RecognizerResult
from analyzer.entity_recognizer import EntityRecognizer
from analyzer.local_recognizer import LocalRecognizer
from analyzer.pattern_recognizer import PatternRecognizer
from analyzer.remote_recognizer import RemoteRecognizer
from analyzer.recognizer_registry.recognizer_registry import RecognizerRegistry
from analyzer.context_enhancer import ContextEnhancer

sys.path.append(os.path.dirname(os.path.dirname(
os.path.abspath(__file__))) + "/analyzer")


from analyzer.analyzer_engine import AnalyzerEngine
