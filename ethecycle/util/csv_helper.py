"""
Helpers for CSV files.
"""

import csv
from typing import Any, List


def write_list_of_lists_to_csv(csv_path: str, objs: List[Any]) -> None:
    """Write objs to csv_path"""
    with open(csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for obj in objs:
            csv_writer.writerow(obj)
