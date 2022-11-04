#!/bin/bash
# Delete everything about the test DB.
pushd tests/file_fixtures/neo4j/data/ >/dev/null
rm -fr dbms databases transactions server_id
popd >/dev/null
