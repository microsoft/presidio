import os
import sys

# bug #602: Fix imports issue in python
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + "/tests")
