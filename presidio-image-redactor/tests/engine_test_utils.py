from typing import Callable

import pytest

def must_succeed(engine_builder: Callable) -> Callable:
    def _must_succeed():
        engine = engine_builder()
        return engine
    return _must_succeed
    
def allow_failure(engine_builder: Callable) -> Callable:
    def _allow_failure():
        try:
            engine = engine_builder()
        except ValueError as e:
            pytest.skip(reason="Could not set up engine, skipping test")
        return engine
    return _allow_failure