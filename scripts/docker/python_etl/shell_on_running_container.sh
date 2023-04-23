CONTAINER_ID=`docker ps -a | grep python_etl | awk '{print $1}'`
docker exec -it $CONTAINER_ID bash -l
