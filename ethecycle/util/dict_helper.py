"""
Help with dicts
"""
from typing import Any, Dict, List, Tuple


def get_dict_key_by_value(_dict: dict, value: Any) -> Any:
    """Inverse of the usual dict operation."""
    return list(_dict.keys())[list(_dict.values()).index(value)]


def sort_dict(_dict: dict) -> List[Tuple[Any, Any]]:
    """Sort dict by value"""
    return sorted(_dict.items(), key=lambda item: item[1], reverse=True)
