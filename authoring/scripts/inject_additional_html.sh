#!/usr/bin/env bash

set -e

ADDITONAL_HTML='<script type="module" crossorigin src="https://k12.openstax.org/apps/raise/index.authoring.7590d6be.js"></script>
<link rel="stylesheet" href="https://k12.openstax.org/apps/raise/index.authoring.377f5e09.css">'

docker compose exec postgres psql -U moodle -d moodle -c "insert into mdl_config (name, value) values('additionalhtmlhead', '$ADDITONAL_HTML') on conflict(name) do update set value='$ADDITONAL_HTML'"
docker compose exec moodle php admin/cli/purge_caches.php
