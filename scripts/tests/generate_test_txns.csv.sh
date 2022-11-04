#!/bin/bash
# Extract rows from whatever SOURCE_TXN_FILE file that actually correspond to rows in the chain_addresses DB

FILE_FIXTURES_DIR=tests/file_fixtures
SOURCE_TXN_FILE=$FILE_FIXTURES_DIR/some_file.csv
GREP_PATTERN_FILE="$FILE_FIXTURES_DIR/interesting_addresses_for_grep.txt"

gunzip $GREP_PATTERN_FILE.gz -k
grep -f $GREP_PATTERN_FILE $FILE_FIXTURES_DIR/$SOURCE_TXN_FILE > $FILE_FIXTURES_DIR/test_txns.csv
rm $GREP_PATTERN_FILE
