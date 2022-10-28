#!/usr/bin/env bash

set -e

ADDITONAL_HTML='<script type="module" crossorigin src="https://k12.openstax.org/apps/raise/index.authoring.7a03beaa.js"></script>
<link rel="stylesheet" href="https://k12.openstax.org/apps/raise/index.authoring.fc0c47d7.css">'

docker compose exec postgres psql -U moodle -d moodle -c "insert into mdl_config (name, value) values('additionalhtmlhead', '$ADDITONAL_HTML') on conflict(name) do update set value='$ADDITONAL_HTML'"
docker compose exec moodle php admin/cli/purge_caches.php
