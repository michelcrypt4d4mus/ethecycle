"""
Helpers for CSV files.
"""
import csv
from typing import Any, List

from rich.text import Text

from ethecycle.util.filesystem_helper import file_size_string
from ethecycle.util.logging import console


def write_list_of_lists_to_csv(csv_path: str, objs: List[Any]) -> None:
    """Write objs to csv_path"""
    with open(csv_path, 'w') as csvfile:
        csv_writer = csv.writer(csvfile)

        for obj in objs:
            csv_writer.writerow(obj)


def print_csv_load_msg(blockchain: str, csv_path: str) -> None:
    msg = Text('Loading ').append(blockchain, style='color(112)').append(' chain ')
    console.print(msg.append(f"transactions from '").append(csv_path, 'green').append("'..."))
    console.print(f"   {file_size_string(csv_path)}", style='dim')
