import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/analyzer")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/analyzer/predefined_recognizers")


from credit_card_recognizer import CreditCardRecognizer
from pattern import Pattern
from pattern_recognizer import PatternRecognizer
