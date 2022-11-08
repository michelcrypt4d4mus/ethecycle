import re
from typing import Any, Union

from pympler.asizeof import asizeof

THOUSAND = 1000
MILLION = THOUSAND * THOUSAND
BILLION = MILLION * 1000
TRILLION = BILLION * 1000

USD_SIZES = [
    (' TRILLION with a T', TRILLION),
    (' billion', BILLION),
    ('M', MILLION),
    ('k', THOUSAND),
    ('', 0)
]

BYTES = 'bytes'
KILOBYTE = 1024
MEGABYTE = 1024 * KILOBYTE
GIGABYTE = 1024 * MEGABYTE

SIZES = {
    'gigabytes': GIGABYTE,
    'megabytes': MEGABYTE,
    'kilobytes': KILOBYTE,
    BYTES: 1,
}


def size_string(number: int) -> str:
    """Build a string representing 'number' as GB/MB/KB/etc."""
    size_str = next(k for k in SIZES.keys() if number > SIZES[k])
    number_str = "{:,.2f}".format(float(number) / SIZES[size_str]) if size_str != BYTES else f"{number}"
    return f"{number_str} {size_str}"


def usd_string(usd: Union[int, float]) -> str:
    """Build a string representing 'number' with M for mil, k for thousand, etc."""
    return f"${comma_format_str(usd)}"


def memsize_string(obj: Any):
    """Build a string representing the in memory size of 'obj'."""
    return size_string(asizeof(obj))


def comma_format_str(number: Union[int, float]) -> str:
    """Build a string representing 'number' with M for mil, k for thousand, etc."""
    size_str, divisor = next(row for row in USD_SIZES if number >= row[1])

    if size_str != '':
        divided = number / divisor

        if divided > 10:
            number_str = "{:,d}".format(int(divided))
        else:
            number_str = "{:,.1f}".format(divided)
    else:
        number_str = int(number)

    return f"{number_str}{size_str}"

def is_even(number: int) -> bool:
    return divmod(number, 2)[1] == 0


def comma_format(number: Union[int, float]) -> str:
    if isinstance(number, float):
        return "{:,.2f}".format(number)
    else:
        return "{:,d}".format(number)


def pct_str(numerator: Union[float, int], denominator: Union[float, int]) -> str:
    return "{:.1f}%".format(pct(numerator, denominator))


def pct(numerator: Union[float, int], denominator: Union[float, int]) -> float:
    if denominator == 0:
        return 0.0
    return 100 * float(numerator) / denominator
