from typing import Any, List, Optional, Sequence, Tuple, Union


def has_intersection(list1: List[Any], list2: List[Any]) -> bool:
    return len(intersection(list1, list2)) > 0


def intersection(list1: List[Any], list2: List[Any]) -> List[Any]:
    return [item for item in list1 if item in list2]


def compare_lists(list1: Sequence, list2: Sequence, column_names: Sequence, ignore_cols: Optional[Sequence] = None) -> str:
    """Compare lists positionally"""
    if len(list1) != len(list2) or len(list2) != len(column_names):
        raise ValueError(f"Can't compare lists of different lengths\ncols:{column_names}\nlist1:{list1}\nlist2:{list2}")

    ignore_cols = ignore_cols or []
    mismatches = []

    for i, col in enumerate(column_names):
        if list1[i] != list2[i] and col not in ignore_cols:
            mismatches.append(f"'{col}' properties ('{list1[i]}' != '{list2[i]}')")

    return '\n    '.join(mismatches)
