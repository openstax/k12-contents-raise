#!/usr/bin/env bash


ACTION=$1

if [ -z "$ACTION" ]; then
    echo "Provide one of the following arguments [up, down, destroy]"
    exit 1
fi

if [ $ACTION == "up" ]; then
    echo "Starting moodle environment"

    docker-compose -f ../authoring/docker/docker-compose.yml up -d
    docker-compose  -f ../authoring/docker/docker-compose.yml exec moodle php admin/cli/install_database.php --agree-license --fullname="Local Dev" --shortname="Local Dev" --summary="Local Dev" --adminpass="admin" --adminemail="admin@acmeinc.com"
    bash  ./../authoring/scripts/inject_additional_html.sh ../authoring/docker/docker-compose.yml
    exit 1
fi

if [ $ACTION == "down" ]; then
    echo "Stoping moodle environment"

    docker-compose -f ../authoring/docker/docker-compose.yml down
    exit 1
fi

if [ $ACTION == "destroy" ]; then
    echo "Destroying moodle environment and state."

    read -p "Are you sure? All database state will be lost. Continue (y/n)? " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        docker-compose -f ../authoring/docker/docker-compose.yml down -v
    fi
    exit 1
fi
