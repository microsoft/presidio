import os
import sys

# pylint: disable=unused-import,wrong-import-position
# bug #602: Fix imports issue in python
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + "/presidio-anonymizer-package")
