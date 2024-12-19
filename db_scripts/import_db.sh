#!/bin/bash

if [[ ! -f $1 ]]; then
    echo 'Error: Please provide the full path to the dump you want to import'
    exit 1
fi

cp "$1" docker_dev/db/dumps
docker exec -it deft_db_1 bash -c "psql -U deft deft < dumps/$(basename "$1")"