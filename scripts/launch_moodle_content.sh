#!/usr/bin/env bash

#up command $1
if [ $1 == "up" ]; then
    echo "Starting moodle environment"
    docker-compose -f ../authoring/docker/docker-compose.yml up -d
    docker-compose  -f ../authoring/docker/docker-compose.yml exec moodle php admin/cli/install_database.php --agree-license --fullname="Local Dev" --shortname="Local Dev" --summary="Local Dev" --adminpass="admin" --adminemail="admin@acmeinc.com"
    exec  ../authoring/scripts/inject_additional_html.sh

    exit 1
fi

if [ $1 == "down" ]; then
    echo "Stoping moodle environment"
    docker-compose -f ../authoring/docker/docker-compose.yml down

    exit 1
fi

if [ $1 == "destroy" ]; then
    echo "Destroying moodle environment and state."
    docker-compose -f ../authoring/docker/docker-compose.yml down -v

    exit 1
fi