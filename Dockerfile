FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

#COPY . .

CMD ["/bin/bash"]


# # Install yarn (TODO: do we need this?)
# RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg -o /root/yarn-pubkey.gpg && apt-key add /root/yarn-pubkey.gpg
# RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" > /etc/apt/sources.list.d/yarn.list

# # Install packages
# RUN apt-get update && apt-get install -y --no-install-recommends \
#         exiftool \
#         imagemagick \
#         iputils-ping \
#         nodejs \
#         pkg-config \
#         postgresql-client \
#         tesseract-ocr \
#         yarn

# # Passed in from docker-compose
# ARG DATABASE_URL
# ARG INSTALL_PATH
# RUN mkdir -p $INSTALL_PATH

# # Install gems
# WORKDIR $INSTALL_PATH
# COPY ./Gemfile ./Gemfile
# COPY ./Gemfile.lock ./Gemfile.lock

# RUN gem install bundler
# RUN bundle install
# RUN yarn install

# # We shouldn't need these Gemfiles anymore; the current ones will be mounted w/the rest of the code
# # RUN rm Gemfile Gemfile.lock
# # RUN rm -fr node_modules

# # For production deploy we would copy everything onto the image
# # COPY ./ .
# WORKDIR /root
# RUN echo 'alias bx="bundle exec "' >> .bash_profile
# CMD ["/bin/bash"]
