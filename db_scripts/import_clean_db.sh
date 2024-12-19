#!/bin/bash

docker exec -it deft_db_1 bash -c "psql -U deft deft < /dumps/clean-2024.sql"
