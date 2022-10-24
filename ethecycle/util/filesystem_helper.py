import importlib.resources
from os import pardir
from pathlib import PosixPath

PROJECT_ROOT_DIR: PosixPath = importlib.resources.files('ethecycle').joinpath(pardir).resolve()
GRAPHML_OUTPUT_DIR = PROJECT_ROOT_DIR.joinpath('output')
DATA_DIR = PROJECT_ROOT_DIR.joinpath('data')
