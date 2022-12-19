# https://www.petekeen.net/archiving-websites-with-wget

wget \
    --mirror \
    --warc-file=silvergate \
    --warc-cdx \
    --page-requisites \
    --html-extension \
    --convert-links \
    --execute robots=off \
    --directory-prefix=. \
    --span-hosts \
    --domains=example.com,www.example.com,cdn.example.com \
    --user-agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15' \
    --wait=10 \
    --random-wait \
    https://www.silvergate.com
