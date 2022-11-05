# bash helper methods for doing stuff with the neo4j container.

# Prints the container ID if running, empty string if not.
running_neo4j_container_id() {
    echo `docker ps | grep neo4j | awk '{print $1}'`
}

# Prints the container ID, bringing up the container if it's not running.
get_neo4j_container_id() {
    local CONTAINER_ID=`running_neo4j_container_id`

    if [[ -z $CONTAINER_ID ]]; then
        echo "neo4j container not running; launching as daemon..." >&2
        docker-compose up neo4j -d
        CONTAINER_ID=`running_neo4j_container_id`
    fi

    echo $CONTAINER_ID
}

# Sets the $NEO4J_CONTAINER_ID variable in the current bash context
set_NEO4J_CONTAINER_ID() {
    NEO4J_CONTAINER_ID=`get_neo4j_container_id`
}

# Run a command on the neo4j container, launching it if it's not running.
run_on_neo4j_container() {
    docker exec --env-file=scripts/docker/neo4j/.env.neo4j -it `get_neo4j_container_id` "$@"
}
