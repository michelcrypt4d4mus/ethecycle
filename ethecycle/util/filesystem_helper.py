import importlib.resources
from os import environ, pardir, path
from pathlib import PosixPath

PROJECT_ROOT_DIR: PosixPath = importlib.resources.files('ethecycle').joinpath(pardir).resolve()
GRAPHML_OUTPUT_DIR = PROJECT_ROOT_DIR.joinpath('output')
DATA_DIR = PROJECT_ROOT_DIR.joinpath('data')

# Token info repo is checked out as part of Dockerfile build process
TOKEN_DATA_DIR = path.join(environ['TOKEN_DATA_PATH'], 'tokens', 'tokens')
