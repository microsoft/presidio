from dataclasses import dataclass
from typing import List


@dataclass
class TextAnalyticsEntityCategory:
    """
    A Category recognized by Text Analytics 'Named entity recognition and PII'.

    The full list can be found here:
    https://docs.microsoft.com/en-us/azure/cognitive-services/text-analytics/named-entity-types?tabs=personal#category-datetime
    """

    name: str
    entity_type: str
    languages: List[str]
    subcategory: str = None
