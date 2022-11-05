#!/bin/bash
# Get bpython REPL on the test version of the python_etl container

cat .env scripts/docker/python_etl/.env.test > scripts/docker/python_etl/.env.test.tmp
docker-compose --env-file scripts/docker/python_etl/.env.test.tmp run --rm python_etl bpython
