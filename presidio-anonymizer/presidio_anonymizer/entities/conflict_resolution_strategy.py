"""An Enum class designed to manage all types of conflicts among entities or text."""
from enum import Enum


class ConflictResolutionStrategy(Enum):
    """Conflict resolution strategy.

    The strategy to use when there is a conflict between two entities.

    TEXT_AND_ENTITIES: The conflict will be resolved on both the output text and the
    output entities level.
    NONE: No conflict resolution will be performed.
    """

    TEXT_AND_ENTITIES = "text_and_entities"
    NONE = "none"
