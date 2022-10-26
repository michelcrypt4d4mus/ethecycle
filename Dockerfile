FROM python:3.10

# Get some bash tools
RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        git

# Pull a reasonably good token data source from github (GIT_REPO_DIR comes from .env)
ARG GIT_REPO_DIR
ENV TOKEN_DATA_REPO_PARENT_DIR=${GIT_REPO_DIR:-/token_data}
RUN mkdir ${TOKEN_DATA_REPO_PARENT_DIR}
WORKDIR ${TOKEN_DATA_REPO_PARENT_DIR}
RUN git clone https://github.com/ethereum-lists/tokens.git

# Install python requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]
