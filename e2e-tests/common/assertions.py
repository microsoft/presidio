import json
from typing import Dict, List, Optional


def equal_json_strings(
    expected: str, actual: str, ignore_keys: Optional[List[str]] = None
):
    if not ignore_keys:
        ignore_keys = []
    return _equal_dicts(
        _ordered(json.loads(expected)),
        _ordered(json.loads(actual)),
        ignore_keys=ignore_keys,
    )


def _equal_dicts(dict1: Dict, dict2: Dict, ignore_keys: List[str]):
    dict1_filtered = {k: v for k, v in dict1.items() if k not in ignore_keys}
    dict2_filtered = {k: v for k, v in dict2.items() if k not in ignore_keys}
    return dict1_filtered == dict2_filtered


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    else:
        return obj
