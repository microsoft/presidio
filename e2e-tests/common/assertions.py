import json


def equal_json_strings(expected, actual):
    return _ordered(json.loads(expected)) == _ordered(json.loads(actual))


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    else:
        return obj
