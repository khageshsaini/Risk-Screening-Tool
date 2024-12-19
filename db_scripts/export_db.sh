#!/bin/bash

dump_name=dump-"$(date +"%d-%m-%Y").sql"
docker exec -it deft_db_1 bash -c "pg_dump -U deft deft > dumps/$dump_name"

if [[ -d $1 ]]; then
  cp "docker_dev/db/dumps/$dump_name" "$1"
fi