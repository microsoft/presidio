import json
from typing import Dict, List, Optional


def equal_json_strings(
    expected: str, actual: str, ignore_keys: Optional[List[str]] = None
):
    if not ignore_keys:
        ignore_keys = []
    return _equal_lists_of_dicts(
        json.loads(expected), json.loads(actual), ignore_keys=ignore_keys
    )


def _equal_lists_of_dicts(
    obj1: List[Dict], obj2: List[Dict], ignore_keys: List[str]
) -> bool:
    if isinstance(obj1, list) and isinstance(obj2, list):
        for v1, v2 in zip(_ordered(obj1), _ordered(obj2)):
            if isinstance(v1, list) and isinstance(v2, list):
                _equal_lists_of_dicts(v1, v2, ignore_keys)
            elif isinstance(v1, dict) and isinstance(v2, dict):
                if not _equal_dicts(v1, v2, ignore_keys):
                    return False
    elif isinstance(obj1, dict) and isinstance(obj2, dict):
        if not _equal_dicts(obj1, obj2, ignore_keys):
            return False

    return True


def _equal_dicts(dict1: Dict, dict2: Dict, ignore_keys: List[str]):
    dict1_filtered = {k: v for k, v in dict1.items() if k not in ignore_keys}
    dict2_filtered = {k: v for k, v in dict2.items() if k not in ignore_keys}
    return _ordered(dict1_filtered) == _ordered(dict2_filtered)


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    else:
        return obj
