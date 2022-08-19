additional_html='<script type="module" crossorigin src="https://k12.openstax.org/apps/raise/index.authoring.8f2edfdb.js"></script>
<link rel="stylesheet" href="https://k12.openstax.org/apps/raise/index.authoring.5bd2c3c5.css">'

docker-compose exec postgres psql -U moodle -d moodle -c "insert into mdl_config('name', 'value') values('additionalhtmlhead', '$additional_html') on conflict('additionalhtmlhead') do update set value=$additional_html