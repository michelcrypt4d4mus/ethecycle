FROM python:3.10

# Get some bash tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        openssh-client \
        sqlite3 \
        wget

# Setup ssh (you need to generate the ssh keys before running docker build; see README.md for details)
ARG SSH_DIR=/root/.ssh
RUN mkdir $SSH_DIR && chmod 700 $SSH_DIR
COPY ./container_id_ed25519 $SSH_DIR/id_ed25519
COPY ./container_id_ed25519.pub $SSH_DIR/id_ed25519.pub

# Pull some wallet tag sources of variable quality from github (GIT_REPO_DIR comes from .env)
ARG GIT_REPO_DIR
ENV TOKEN_DATA_REPO_PARENT_DIR=${GIT_REPO_DIR:-/token_data}
RUN mkdir ${TOKEN_DATA_REPO_PARENT_DIR}
WORKDIR ${TOKEN_DATA_REPO_PARENT_DIR}
RUN git clone https://github.com/ethereum-lists/tokens.git
# Ether scrapes
RUN git clone https://github.com/brianleect/etherscan-labels.git
RUN git clone https://github.com/W-McDonald/etherscan.git
# Trustwallet assets
RUN git clone https://github.com/trustwallet/assets trustwallet_assets
RUN rm -fr trustwallet_assets/.git && find trustwallet_assets/ -name '*.png' -delete
# Pull Adamant vaults
RUN git clone https://github.com/eepdev/vaults.git
# Pull "hop airdrop" blacklists?  not sure what this is
RUN git clone https://github.com/rchen8/hop-airdrop.git
# More wallets
RUN git clone https://github.com/Mmoouu/test-iotxview/
RUN rm -fr test-iotxview/.git && find test-iotxview/ -name '*.png' -delete
# Even more wallets
RUN git clone https://github.com/hylsceptic/ethereum_parser.git
RUN git clone https://github.com/yaocg/uniswap-arbitrage.git
RUN git clone https://github.com/m-root/arb-trading.git
RUN git clone https://github.com/Inka-Finance/assets.git
RUN rm -fr assets/.git && find assets/ -name '*.png' -delete
RUN git clone https://github.com/aurafinance/aura-token-allocation.git
RUN git clone https://github.com/kovart/forta-agents.git
RUN git clone https://github.com/graphsense/graphsense-tagpacks.git
# Tron wallets
RUN git clone https://github.com/oushu1zhangxiangxuan1/TronStreaming.git
RUN rm -fr TronStreaming/.git

# Python env vars
WORKDIR /python
ENV ETHECYCLE_ENV=development \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_HOME="/python/poetry" \
    POETRY_NO_INTERACTION=1

# Install poetry. Lots of ideas as to how to approach this here: https://stackoverflow.com/questions/53835198/integrating-python-poetry-with-docker
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"
RUN poetry config virtualenvs.create false
COPY poetry.lock pyproject.toml ./
RUN poetry install $(test "$ETHECYCLE_ENV" == production && echo "--no-dev")

# Remove unnecessaries
RUN apt-get purge --auto-remove -y \
        curl \
        wget

CMD ["/bin/bash"]
