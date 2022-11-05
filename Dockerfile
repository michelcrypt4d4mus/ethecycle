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
ENV CHAIN_ADDRESS_DATA_DIR=/chain_address_data
RUN mkdir ${CHAIN_ADDRESS_DATA_DIR}
WORKDIR ${CHAIN_ADDRESS_DATA_DIR}

# Pull Adamant vaults
RUN git clone https://github.com/eepdev/vaults.git && \
    git clone https://github.com/rchen8/hop-airdrop.git && \
    git clone https://github.com/Mmoouu/test-iotxview/ && \
    git clone https://github.com/hylsceptic/ethereum_parser.git && \
    git clone https://github.com/yaocg/uniswap-arbitrage.git && \
    git clone https://github.com/m-root/arb-trading.git && \
    git clone https://github.com/Inka-Finance/assets.git && \
    git clone https://github.com/aurafinance/aura-token-allocation.git && \
    git clone https://github.com/kovart/forta-agents.git && \
    git clone https://github.com/graphsense/graphsense-tagpacks.git && \
    git clone https://github.com/oushu1zhangxiangxuan1/TronStreaming.git

# Remove some unnecessary cruft from image
RUN rm -fr test-iotxview/.git && find test-iotxview/ -name '*.png' -delete && \
    rm -fr assets/.git && find assets/ -name '*.png' -delete && \
    rm -fr TronStreaming/.git

# Build a minimal .sqliterc config file
ARG SQLITE_RC=/root/.sqliterc
RUN echo '.mode table' > ${SQLITE_RC} && echo '.header on' >> ${SQLITE_RC}

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
# Create an entrypoint.sh that runs 'poetry install' which is needed for pytest (TODO: why?)
RUN echo '#!/bin/bash\npoetry install\nexec "$@"' > ./entrypoint.sh && chmod 774 ./entrypoint.sh

# TODO: Put a temporary copy of repo on the image and bake the chain addresses database into the image
WORKDIR /ethecycle_build_address_db
COPY ./ ./
RUN IS_DOCKER_IMAGE_BUILD=True ./import_chain_addresses.py ALL
WORKDIR /python
RUN rm -fr /ethecycle_build_address_db

# Remove unnecessaries
RUN apt-get purge --auto-remove -y \
        wget

ENTRYPOINT ["/python/entrypoint.sh"]
CMD ["/bin/bash"]
