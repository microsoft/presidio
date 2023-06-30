from presidio_anonymizer.operators import OperatorsFactory

from functools import wraps
import sys

def setup_function(function):
    b = hasattr(function, '__wrapped__')
    if not b:
        return
    b = hasattr(function.__wrapped__, '__custom_operator__')
    if not b:
        return

    resetOperatorsFactory()

def teardown_function(function):
    b = hasattr(function, '__wrapped__')
    if not b:
        return
    b = hasattr(function.__wrapped__, '__custom_operator__')
    if not b:
        return

    resetOperatorsFactory()

def resetOperatorsFactory():
    OperatorsFactory._operator_class = None  # cleanup
    OperatorsFactory._anonymizers = None  # simulates first run
    OperatorsFactory._deanonymizers = None # simulates first run
    try:
         from tests.operators.mock_operators import Encrypt2, Encrypt3, Decrypt2, Decrypt3
         del Encrypt2, Encrypt3, Decrypt2, Decrypt3
    except KeyError:
        pass


def custom_indirect_operator(f):
    @wraps(f)
    def new_f(*arg, **kwargs):
        f(*arg, **kwargs)
    f.__custom_operator__ = True
    return new_f
