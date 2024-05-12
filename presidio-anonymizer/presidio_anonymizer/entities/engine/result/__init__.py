"""Engine result items either for anonymize or decrypt."""

from .operator_result import OperatorResult  # isort:skip
from .engine_result import EngineResult

__all__ = [
    "OperatorResult",
    "EngineResult",
]
