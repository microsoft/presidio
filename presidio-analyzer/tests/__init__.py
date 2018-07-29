import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))+"/analyzer")

from analyzer import matcher
match = matcher.Matcher()
