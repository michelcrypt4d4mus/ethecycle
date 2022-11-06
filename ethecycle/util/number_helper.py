from typing import Any, Union

from pympler.asizeof import asizeof

MILLION = 1000000
BILLION = MILLION * 1000

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


def memsize_string(obj: Any):
    """Build a string representing the in memory size of 'obj'."""
    return size_string(asizeof(obj))


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
