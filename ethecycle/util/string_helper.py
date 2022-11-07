"""
String utilities.
"""
from typing import Any, Callable, Iterable, Optional

from ethecycle.util.logging import log


def quoted_join(_list: Iterable[Any], quote_char: str = "'", separator: str = ', ', func: Callable = str) -> str:
    """
    Return a comma separated list of strings quoted by 'quote_char'. If 'func' arg is provided
    the output of calling it on each element of the list will be used instead of str().
    """
    quoted_list = [f"{quote_char}{func(item)}{quote_char}" for item in _list]
    return separator.join(quoted_list)


def strip_and_set_empty_string_to_none(_str: Optional[str], to_lowercase: bool = False) -> Optional[str]:
    """Strip whitespace/optionally downcase. Return None if resultant string is empty, otherwise return stripped string."""
    if _str is None:
        return None
    elif isinstance(_str, str):
        stripped_str = _str.strip()

        if len(stripped_str) == 0:
            return None

        return stripped_str.lower() if to_lowercase else stripped_str
    else:
        log.warning(f"'{_str}' is not a string")
        return _str
