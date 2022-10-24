FROM python:3

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        git

# Pull a reasonably good token data source from github (TOKEN_DATA_DIR comes from .env)
ARG TOKEN_DATA_DIR
ENV TOKEN_DATA_PATH=${TOKEN_DATA_DIR:-/token_data}
RUN mkdir ${TOKEN_DATA_PATH}
WORKDIR ${TOKEN_DATA_PATH}
RUN git clone https://github.com/ethereum-lists/tokens.git

# Install python requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]
