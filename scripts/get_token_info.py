from subprocess import check_call

from ethecycle.util.filesystem_helper import DATA_DIR

TOKEN_INFO_REPO = 'https://github.com/ethereum-lists/tokens.git'
CHECKOUT_CMD = f"cd {DATA_DIR} && git clone {TOKEN_INFO_REPO}"

#GIT_CHECKOUT_DIR=


#
