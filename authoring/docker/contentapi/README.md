# Content API

This is a simple `contentapi` to be used by the authoring Moodle build in this repo. If you want the service to return a specific piece of content, you can place a file `{content_id}.html` in this directory and it will pick it up. If an invalid content ID is trying to be reached this endpoint will return a 404 error.