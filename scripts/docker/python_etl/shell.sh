#!/bin/bash
# Get a bash shell on python_etl container. Container will be launched if not currently running.
CONTAINER_ID=`docker ps | grep python_etl | awk '{print $1}'`
docker exec -it $CONTAINER_ID bash -l
# docker-compose run --rm python_etl
