"""Initializing all the existing anonymizers."""
from .operator import OperatorType, Operator
from .operators_factory import OperatorsFactory

__all__ = ["OperatorType",
           "Operator",
           "OperatorsFactory"]
