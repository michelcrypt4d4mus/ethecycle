# https://www.petekeen.net/archiving-websites-with-wget
#  -- level is Recursion depth

wget \
    --mirror \
    --warc-cdx \
    --page-requisites \
    --html-extension \
    --convert-links \
    --execute robots=off \
    --directory-prefix=. \
    --span-hosts \
    --user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15' \
    --wait=10 \
    --random-wait \
    --recursive \
    --no-parent \
    --warc-file=docs.strikeprotocols.com \
    --domains=docs.strikeprotocols.com \
    --level=5 https://docs.strikeprotocols.com

