#!/bin/bash
# Get a bash shell on the test container

docker-compose --env-file .env.test run --rm python_etl
