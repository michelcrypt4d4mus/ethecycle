FROM python:3

ARG TOKEN_DATA_PATH=/token_data

RUN apt-get update && apt-get install -y --no-install-recommends \
        wget \
        git

# Pull a reasonably good token data source from github
RUN mkdir ${TOKEN_DATA_PATH}
WORKDIR ${TOKEN_DATA_PATH}
RUN git clone https://github.com/ethereum-lists/tokens.git

# Install python requirements
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash"]
