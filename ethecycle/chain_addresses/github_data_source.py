"""
Some wallet/token data imports require data to be pulled from GitHub.
Some of those repos are quite large so rather than just preload them
all on the docker image, we pull them only on demand.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from shutil import rmtree
from subprocess import check_output
from typing import Optional
from urllib.parse import urljoin

from ethecycle.config import Config
from ethecycle.util.filesystem_helper import SCRIPTS_DIR
from ethecycle.util.logging import log

GIT_PULL_SCRIPT = SCRIPTS_DIR.joinpath('chain_addresses').joinpath('git_clone_if_missing.sh')
GITHUB_URL = 'https://github.com/'
DOT_GIT = '.git'


@dataclass
class GithubDataSource:
    """'repo_url' is only user/repo e.g. 'eth-list/token' not 'https://github.com/eth-list/token.git'."""
    repo_url: str
    folder_name: Optional[str] = None

    @contextmanager
    def local_repo_path(self):
        """Returns path to repo. Pull the data from github if needed."""
        repo_url = urljoin(GITHUB_URL, self.repo_url) + DOT_GIT
        cmd = f"{GIT_PULL_SCRIPT} {repo_url} {self.folder_name if self.folder_name else ''}"
        local_repo_dir = check_output(cmd.split()).decode().rstrip()
        log.info(f"Pulled '{repo_url}' to local folder '{local_repo_dir}'")
        yield local_repo_dir

        # Remove the repo if this is being done during the docker image build.
        if Config.is_docker_image_build:
            log.info(f"Deleting '{local_repo_dir}'...")
            rmtree(local_repo_dir)
