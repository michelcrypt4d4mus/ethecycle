FROM python:3.10

# Get some bash tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        git \
        openssh-client \
        wget

# Pull a reasonably good token data source from github (GIT_REPO_DIR comes from .env)
ARG GIT_REPO_DIR
ENV TOKEN_DATA_REPO_PARENT_DIR=${GIT_REPO_DIR:-/token_data}
RUN mkdir ${TOKEN_DATA_REPO_PARENT_DIR}
WORKDIR ${TOKEN_DATA_REPO_PARENT_DIR}
RUN git clone https://github.com/ethereum-lists/tokens.git

# Install poetry
WORKDIR /usr/src/app
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH "$PATH:/root/.local/bin"

# Install python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Setup ssh (you need to generate the ssh keys before running docker build; see README.md for details)
ARG SSH_DIR=/root/.ssh
RUN mkdir $SSH_DIR
RUN chmod 700 $SSH_DIR
COPY ./container_id_ed25519 $SSH_DIR/id_ed25519
COPY ./container_id_ed25519.pub $SSH_DIR/id_ed25519.pub

CMD ["/bin/bash"]
