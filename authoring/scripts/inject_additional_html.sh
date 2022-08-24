#!/usr/bin/env bash

set -e

COMPOSE_FILE=$1

if [ -z "$COMPOSE_FILE" ]; then
    echo "Provide input docker-compose.yml file path"
    exit 1
fi

ADDITONAL_HTML='<script type="module" crossorigin src="https://k12.openstax.org/apps/raise/index.authoring.56ae0462.js"></script>
<link rel="stylesheet" href="https://k12.openstax.org/apps/raise/index.authoring.5bd2c3c5.css">'
# File path to docker-compose -f argument is reletive to the script launch_moodle_contents.sh.
docker-compose -f $COMPOSE_FILE exec postgres psql -U moodle -d moodle -c "insert into mdl_config (name, value) values('additionalhtmlhead', '$ADDITONAL_HTML') on conflict(name) do update set value='$ADDITONAL_HTML'"

docker-compose -f $COMPOSE_FILE exec moodle php admin/cli/purge_caches.php
