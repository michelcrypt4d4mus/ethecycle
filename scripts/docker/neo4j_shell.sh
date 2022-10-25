docker-compose up neo4j -d
NEO4J_CONTAINER_ID=`docker ps | grep neo4j | awk '{print $1}'`
docker exec --env-file=.env -it $NEO4J_CONTAINER_ID bash -l
