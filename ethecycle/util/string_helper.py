"""
String utilities.
"""
import re
from typing import Any, Callable, Iterable, List, Optional
from urllib.parse import parse_qs

from ethecycle.util.logging import log
from ethecycle.util.string_constants import ALPHABET_UPPER, HTTPS, SOCIAL_MEDIA_URLS

FACEBOOK_PROFILE_PHP = 'facebook.com/profile.php'
MAX_WALLET_NAME_LENGTH = 60
HALF_MAX_WALLET_NAME_LENGTH = int(MAX_WALLET_NAME_LENGTH / 2) - 5
USD_REGEX = re.compile('^\\$?[\\d,]+(?:\\.\\d{2})?$')
INTEGER_REGEX = re.compile('^[\\d,]$')


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


def extract_wallet_name(name: str) -> str:
    """Turns a random string into something we'd want to use as a wallets.name entry."""
    if name is None:
        return None
    elif not isinstance(name, str):
        name = str(name)

    name = name.removeprefix(HTTPS).removeprefix('http://').removeprefix('www.').removeprefix('mobile.')

    if has_as_substring(name, SOCIAL_MEDIA_URLS):
        name = name.removeprefix('m.')

        if name.startswith(FACEBOOK_PROFILE_PHP) and '&' in name:
            id = parse_qs(name).get('id')

            if id:
                name = f"{FACEBOOK_PROFILE_PHP}?id={id[0]}"
        else:
            name = name.split('?')[0].strip()

    if len(name) > MAX_WALLET_NAME_LENGTH:
        name = name[0:HALF_MAX_WALLET_NAME_LENGTH] + '...<snip>...' + name[-HALF_MAX_WALLET_NAME_LENGTH:]

    return name


def has_as_substring(search_string: str, substrings: List[str], ignore_case: bool = False) -> bool:
    """Returns True if any members of 'substrings' appear in 'search_string'."""
    if ignore_case:
        substrings = [s.lower() for s in substrings]
        search_string = search_string.lower()

    return any(substring in search_string for substring in substrings)


def get_nth_alphabet_char(n: int) -> str:
    """Wraps to AA, BB, then AAA, etc."""
    result = divmod(n, 26)
    char = ALPHABET_UPPER[result[1]]
    return char * (result[0] + 1)


def append_nth_alphabet_char(_str: str, n: int) -> str:
    return f"{_str} {get_nth_alphabet_char(n)}"


def is_usd(_str: str) -> bool:
    return USD_REGEX.match(_str) is not None


def is_integer(_str: str) -> bool:
    return INTEGER_REGEX.match(_str) is not None
