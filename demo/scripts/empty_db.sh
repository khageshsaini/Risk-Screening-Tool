#!/bin/bash

docker exec -it deft_db_1 bash -c '
psql -U deft deft <<EOF
    DELETE FROM event_tags;
    DELETE FROM weather_data_variables;
    DELETE FROM weather_data;
    DELETE FROM power_systems;
    DELETE FROM stations;
    DELETE FROM station_locations;
    DELETE FROM files_users;
    DELETE FROM files;
    DELETE FROM risk_models;
    DELETE FROM technologies;
    DELETE FROM projects;
    DELETE FROM resources;
    DELETE FROM raw_weather_data;
EOF
'
