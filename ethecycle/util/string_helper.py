"""
String utilities.
"""
from typing import Any, Callable, Iterable


def quoted_join(_list: Iterable[Any], quote_char: str = "'", separator: str = ', ', func: Callable = str) -> str:
    """
    Return a comma separated list of strings quoted by 'quote_char'. If 'func' arg is provided
    the output of calling it on each element of the list will be used instead of str().
    """
    quoted_list = [f"{quote_char}{func(item)}{quote_char}" for item in _list]
    return separator.join(quoted_list)

