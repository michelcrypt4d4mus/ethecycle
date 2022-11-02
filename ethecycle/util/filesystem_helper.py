import gzip
import importlib.resources
import os
import re
import shutil
from datetime import datetime
from os import path
from pathlib import Path, PosixPath
from subprocess import check_call
from typing import List, Optional, Union

from ethecycle.util.logging import console
from ethecycle.util.num_helper import size_string

# Dirs inside package structure
PACKAGE_DIR = importlib.resources.files('ethecycle')
DATA_DIR = PACKAGE_DIR.joinpath('data')
CHAIN_ADDRESSES_DIR = DATA_DIR.joinpath('chain_addresses')
DB_DIR = CHAIN_ADDRESSES_DIR.joinpath('db')
RAW_DATA_DIR = CHAIN_ADDRESSES_DIR.joinpath('raw_data')

# Dirs outside package structure
PROJECT_ROOT_DIR: PosixPath = PACKAGE_DIR.joinpath(os.pardir).resolve()
OUTPUT_DIR = PROJECT_ROOT_DIR.joinpath('output')
SCRIPTS_DIR = PROJECT_ROOT_DIR.joinpath('scripts')

# If files are really big we automatically split them up for loading
SPLIT_FILES_DIR = OUTPUT_DIR.joinpath('tmp')
DEFAULT_LINES_PER_FILE = 250000
ETHECYCLE_DIR = '/ethecycle'
GZIP_EXTENSION = '.gz'

# Token info repo is checked out as part of Dockerfile build process
# TODO: rename to TOKEN_AND_WALLET_REPOS_DIR
TOKEN_DATA_REPO_PARENT_DIR = os.environ['TOKEN_DATA_REPO_PARENT_DIR']


def files_in_dir(dir: Union[str, PosixPath], with_extname: Optional[str] = None) -> List[str]:
    """paths for non dot files, optionally ending in 'with_extname'"""
    files = [path.join(dir, file) for file in os.listdir(dir) if not file.startswith('.')]
    files = [file for file in files if not path.isdir(file)]

    if with_extname:
        files = [f for f in files if f.endswith(f".{with_extname}")]

    return files


def get_lines(file_path: str, comment_char: Optional[str] = '#') -> List[str]:
    """Get lines from text or gzip file optionally skipping lines starting with comment_char."""
    if file_path.endswith(GZIP_EXTENSION):
        with gzip.open(file_path, 'rb') as file:
            lines = [line.decode().rstrip() for line in file]
    else:
        with open(file_path, 'r') as file:
            lines = file.readlines()

    if comment_char:
        lines = [line for line in lines if not line.startswith(comment_char)]

    return lines


def file_size_string(file_path: str) -> str:
    return "File size: " + size_string(path.getsize(file_path))


def is_running_in_container() -> bool:
    """Hacky way to guess if we're in a container or on the OS."""
    return str(PROJECT_ROOT_DIR).startswith(ETHECYCLE_DIR)


def system_path_to_container_path(file_path: str):
    """Take a file_path on the broader system and turn it into one accessible from inside containers."""
    return re.sub(f".*{ETHECYCLE_DIR}", ETHECYCLE_DIR, str(file_path))


def timestamp_for_filename() -> str:
    """Returns a string showing current time in a file name friendly format."""
    return datetime.now().strftime("%Y-%m-%dT%H.%M.%S")


def split_big_file(file_path: str, lines_per_file: int = DEFAULT_LINES_PER_FILE) -> List[str]:
    """Copies the file to a tmp dir, splits it up, and returns list of files that resulted from the split."""
    file_basename = path.basename(file_path)
    file_basename_no_ext = Path(file_path).stem
    split_files_dir = SPLIT_FILES_DIR.joinpath(f"split_{file_basename_no_ext}")
    copied_file_path = split_files_dir.joinpath(file_basename)
    split_cmd = f"split -d -l {lines_per_file} {file_basename} {file_basename}."

    if not path.isdir(SPLIT_FILES_DIR):
        console.print(f"Creating tmp dir for split files: '{SPLIT_FILES_DIR}'...", style='dim')
        os.mkdir(SPLIT_FILES_DIR)

    if not path.isdir(split_files_dir):
        console.print(f"Creating dir for results of splitting big file: '{split_files_dir}'", style='dim')
        os.mkdir(split_files_dir)

    console.print(f"Copying '{file_path}' to '{copied_file_path}'...", style='dim')
    shutil.copy(file_path, copied_file_path)

    # Do the split
    current_working_dir = os.getcwd()
    os.chdir(split_files_dir)
    console.print(f"Running: '{split_cmd}' in '{split_files_dir}'...", style='dim')
    check_call(split_cmd.split(' '))
    console.print(f"Splitting file complete; removing '{copied_file_path}'...", style='dim')
    os.chdir(current_working_dir)
    os.remove(copied_file_path)

    # Collect files
    files = files_in_dir(str(split_files_dir))
    console.print(f"{len(files)} files resulted from the split.")
    return files
