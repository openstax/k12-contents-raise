#!/usr/bin/env bash

export COMPOSE_FILE=../authoring/docker/docker-compose.yml

ACTION=$1

if [ -z "$ACTION" ]; then
    echo "Provide one of the following arguments [up, down, destroy]"
    exit 1
fi

if [ $ACTION == "up" ]; then
    echo "Starting authoring environment"

    docker-compose up -d
    docker-compose exec moodle php admin/cli/install_database.php --agree-license --fullname="Local Dev" --shortname="Local Dev" --summary="Local Dev" --adminpass="admin" --adminemail="admin@acmeinc.com"
    docker-compose exec postgres psql -U moodle -d moodle -c "update mdl_config set value='1' where name='forcelogin'"

    bash  ./../authoring/scripts/inject_additional_html.sh
    exit 0
fi

if [ $ACTION == "down" ]; then
    echo "Stoping authoring environment"

    docker-compose down
    exit 0
fi

if [ $ACTION == "destroy" ]; then
    echo "Destroying authoring environment and state."

    read -p "Are you sure? All database state will be lost. Continue (y/n)? " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        docker-compose down -v
    fi
    exit 0
fi
