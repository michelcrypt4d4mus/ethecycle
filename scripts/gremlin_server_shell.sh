docker-compose up tinkerpop -d
GREMLIN_CONTAINER_ID=`docker ps | grep tinkerpop | awk '{print $1}'`
docker exec --env-file=.env -it $GREMLIN_CONTAINER_ID bash -l
