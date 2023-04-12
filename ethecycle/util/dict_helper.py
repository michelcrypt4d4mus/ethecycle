"""
Help with dicts
"""
import logging
from typing import Any, Dict, Generator, Iterator, List, Optional, Tuple


def get_dict_key_by_value(_dict: dict, value: Any) -> Any:
    """Inverse of the usual dict operation."""
    return list(_dict.keys())[list(_dict.values()).index(value)]


def sort_dict(_dict: dict) -> List[Tuple[Any, Any]]:
    """Sort dict by value"""
    return sorted(_dict.items(), key=lambda item: item[1], reverse=True)


def walk_json(obj: Any, parent_keys: Optional[str] = None) -> Iterator[Tuple[Optional[str], str]]:
    """
    Walk down a dict to the bottom and yield each hierarchy of keys as well as bottom values.
    'parent_keys' is a string of form "key1.key2.key3"
    """
    if isinstance(obj, (int, float, str)):
        logging.debug(f"THIS WAS A CONSTANT, NOT A dict!\n{obj}")
        yield(parent_keys, str(obj))

    elif isinstance(obj, (tuple, list)):
        logging.debug(f"THIS WAS A LIST, NOT A dict!\n{obj}")
        for idx, e in enumerate(obj):
            if parent_keys is not None:
                parent_key = f"{parent_keys}[{idx}]"
            else:
                parent_key = str(idx)

            for k, v in walk_json(e, parent_key):
                if isinstance(v, (int, float, str)):
                    yield(k, v)
                else:
                    for _k, _v in walk_json(v):
                        yield(_k, _v)


    elif isinstance(obj, dict):
        logging.debug(f"THIS A DICT!")
        for k, v in obj.items():
            if parent_keys is not None:
                parent_key = f"{parent_keys}.{k}"
            else:
                parent_key = k

            if isinstance(v, (int, float)):
                logging.debug('value is number...')
                return (None, None)
            elif isinstance(v, (str)):
                logging.debug('value is str...')
                yield(parent_key, v)
            elif isinstance(v, (tuple, list)):
                logging.debug('value is tuple...')
                for idx, array_val in walk_json(v, parent_key):
                    yield(f"{parent_key}[{idx}]", array_val)
            elif isinstance(v, dict):
                logging.debug("value is dict...")
                for _k, _v in walk_json(v, parent_key):
                    if _k is None:
                        return

                    yield(_k, _v)
            else:
                raise ValueError(f"Got key, value of '{k}' ({type(k)}): '{v} ({type(v)})'")

    else:
        raise ValueError(f"Obj '{obj}' of unknown type {type(obj)}")
