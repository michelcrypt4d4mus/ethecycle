from typing import Any, List


def has_intersection(list1: List[Any], list2: List[Any]) -> bool:
    return len(intersection(list1, list2)) > 0


def intersection(list1: List[Any], list2: List[Any]) -> List[Any]:
    return [item for item in list1 if item in list2]
