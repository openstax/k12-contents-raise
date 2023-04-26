#!/usr/bin/env bash

export COMPOSE_FILE=./authoring/docker/docker-compose.yml

ACTION=$1

help () {
    echo "
    Commands

    up             Start the authoring environment
    down           Stop the authoring environment
    destroy        Stop the authoring environment and destroy all state.
    set-variant    Configure content variant used for preview
    reset-variant  Reset variant used for preview to default
    create-variant Create a variant HTML file for page
    start-editing  Initialize environment for new round of edits
    "
}

start_env () {
    docker compose up --build -d
    docker compose exec moodle ./wait-for-it.sh postgres:5432 -- php admin/cli/install_database.php --agree-license --fullname="Local Dev" --shortname="Local Dev" --summary="Local Dev" --adminpass="admin" --adminemail="admin@acmeinc.com"
    docker compose exec postgres psql -U moodle -d moodle -c "update mdl_config set value='1' where name='forcelogin'"
    bash  ./authoring/scripts/inject_additional_html.sh
}

destroy_env() {
    docker compose down -v
}

if [ $# -eq 0 ]; then
    help
    echo "Please provide one of the valid commands."
    exit 1
fi

if [ "$ACTION" == "up" ]; then
    echo "Starting authoring environment"

    start_env

    exit 0
fi

if [ "$ACTION" == "down" ]; then
    echo "Stoping authoring environment"

    docker compose down
    exit 0
fi

if [ "$ACTION" == "destroy" ]; then
    echo "Destroying authoring environment and state."

    read -p "Are you sure? All database state will be lost. Continue (y/n)? " -n 1 -r
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        destroy_env
    fi
    exit 0
fi

if [ "$ACTION" == "set-variant" ]; then
    VARIANT=$2

    if [[ -z $VARIANT ]]; then
        echo "Please provide a variant name"
        exit 1
    fi

    set -e

    sed 's/CONTENT_VARIANT=.*/CONTENT_VARIANT='"$VARIANT"'/' ./authoring/docker/.env > ./authoring/docker/.env.variant
    docker compose --env-file ./authoring/docker/.env.variant up --build -d

    exit 0
fi

if [ "$ACTION" == "reset-variant" ]; then
    set -e

    docker compose up --build -d

    exit 0
fi

if [ "$ACTION" == "create-variant" ]; then
    VARIANT=$2
    UUID=$3

    if [[ -z $UUID ]] || [[ -z $VARIANT ]]; then
        echo "Please provide UUID and variant name arguments. For example: create-variant {variant} {UUID}"
        exit 1
    fi

    if [[ ! -e "./html/$UUID.html" ]]; then
        echo "File ./html/$UUID.html does not exist!"
        exit 1
    fi

    VARIANT_FILE_PATH="./html/$UUID/$VARIANT.html"

    if [[ -e "$VARIANT_FILE_PATH" ]]; then
        echo "File $VARIANT_FILE_PATH already exists!"
        exit 1
    fi

    set -e

    mkdir -p "./html/$UUID"
    cp "./html/$UUID.html" "$VARIANT_FILE_PATH"
    echo "Created variant file $VARIANT_FILE_PATH"

    if which "code"; then
        # Open file if command is available on path
        code "$VARIANT_FILE_PATH"
    fi

    exit 0
fi

if [ "$ACTION" == "start-editing" ]; then
    NAME=$2

    if [ -n "$(git status --untracked-files=no --porcelain)" ]; then
        echo "WARNING: It looks like you have uncommitted changes currently. Please commit, stash, or clean and try again so the changes are not unintentionally lost."
        exit 1
    fi

    if [[ -z $NAME ]]; then
        echo "Please provide a branch name to create for tracking edits"
        exit 1
    fi

    if git rev-parse --verify --quiet refs/heads/"$NAME"; then
        echo "The provided branch name already exists! Please provide a unique name or delete the existing branch."
        exit 1
    fi

    set -e

    git checkout main
    git pull
    git checkout -b "$NAME"
    destroy_env
    start_env
    bash ./scripts/create_mbz_files.sh
    docker compose cp "raise-$(git rev-parse --short HEAD).mbz" moodle:/var/www/html/raise.mbz
    rm "raise-$(git rev-parse --short HEAD).mbz"
    docker compose exec moodle php admin/cli/restore_backup.php --file=/var/www/html/raise.mbz --categoryid=1

    echo "Your environment is ready for editing!"

    exit 0
fi

help
echo "Invalid command. Please provide one of the valid commands."
exit 1
