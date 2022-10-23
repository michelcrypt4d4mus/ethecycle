from typing import Any

from pympler.asizeof import asizeof

BYTES = 'bytes'

SIZES = {
    'gigabytes': 1024 * 1024 * 1024,
    'megabytes': 1024 * 1024,
    'kilobytes': 1024,
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