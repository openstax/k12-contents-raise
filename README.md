# K12 Content - RAISE

This repository contains course content for the RAISE project.

## Generating MBZ files for import into Moodle

In order to import content from this repository into Moodle, you can run the `create_mbz.sh` script:

```bash
$ ./scripts/create_mbz.sh
```

The script will generate files with a git short ref in the filename so it's clear what content version was used to generate the file.
