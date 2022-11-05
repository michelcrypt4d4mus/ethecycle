#!/bin/bash
# Ask neo4j-admin for recommended JVM memory settings.
# See: https://neo4j.com/docs/operations-manual/5/tools/neo4j-admin/neo4j-admin-memrec/
#      https://neo4j.com/docs/operations-manual/current/docker/operations/#docker-neo4j-memrec

SCRIPT_PATH=$(dirname -- "$(readlink -f -- "$0";)";)

show_help() {
    cat << EOF

Usage: ${0##*/} [-h] [MEMORY_STRING]

Generate a .neo4j.env file with recommended Java memory settings for running neo4j in a docker image.
    If MEMORY_STRING arg is provided it must be comprised of a number and a letter, e.g. '2g' or '512m'
    If MEMORY_STRING is not provided it defaults to the allocated memory for the 'neo4j' container as read from 'docker stats'.

        -h, --help      show this usage message

See https://neo4j.com/docs/operations-manual/5/tools/neo4j-admin/neo4j-admin-memrec/ for more info.

EOF
}


# Find the neo4j container
docker-compose up -d
. $SCRIPT_PATH/neo4j_container_helper.sh
set_NEO4J_CONTAINER_ID

# Set up the MEMORY_STRING arg or use defaults 'from docker stats'
if [[ -z $1 ]]; then
    echo "MEMORY_STRING arg not provided; defaulting to value given by 'docker stats'..."
    MEMORY_STRING=$(docker stats --no-stream $NEO4J_CONTAINER_ID | grep $NEO4J_CONTAINER_ID | awk '{print $6}')
    MEMORY_STRING=${MEMORY_STRING%iB}
    echo "Neo4j allocated memory: $MEMORY_STRING"
elif [[ $1 == -h ]]; then
    show_help
    exit
elif [[ ! $1 =~ ^[0-9.]+[gkmGKM]$ ]]; then
    echo "'$1' is an invalid value for MEMORY_STRING"
    show_help
    exit 1
else
    MEMORY_STRING=$1
fi

# Execute neo4j-admin server memory-recommendation on the container
NEO4J_ENV_FILE="$SCRIPT_PATH/.env.neo4j"
run_on_neo4j_container /var/lib/neo4j/bin/neo4j-admin server memory-recommendation --memory=$MEMORY_STRING --docker > $NEO4J_ENV_FILE

echo -e "\nOfficial neo4j-admin recommendations:\n"
grep -v "#" "$NEO4J_ENV_FILE"
echo -e "\nRecommendations written to '$NEO4J_ENV_FILE'.\n"
