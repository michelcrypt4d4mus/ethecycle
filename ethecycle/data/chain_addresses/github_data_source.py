"""
Some wallet/token data imports require data to be pulled from GitHub.
Some of those repos are quite large so rather than just preload them
all on the docker image, we pull them only on demand.
"""
from dataclasses import dataclass
from subprocess import check_output
from typing import Optional

from ethecycle.util.filesystem_helper import SCRIPTS_DIR

GIT_PULL_SCRIPT = SCRIPTS_DIR.joinpath('chain_addresses').joinpath('git_clone_if_missing.sh')


@dataclass
class GithubDataSource:
    repo_url: str
    folder_name: Optional[str] = None

    def local_repo_path(self) -> str:
        """Returns path to repo. Pull the data from github if needed."""
        cmd = f"{GIT_PULL_SCRIPT} {self.repo_url} {self.folder_name if self.folder_name else ''}"
        return check_output(cmd.split()).decode().rstrip()
