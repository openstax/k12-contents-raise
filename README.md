# K12 Content - RAISE

This repository contains course content for the RAISE project.

## Generating MBZ files for import into Moodle

In order to import content from this repository into Moodle, you can run the `create_mbz.sh` script:

```bash
$ ./scripts/create_mbz_files.sh
```

The script will generate files with a git short ref in the filename so it's clear what content version was used to generate the file.

## Import `mbz` content

The content in the `mbz` directory of this repo can be updated given an input `.mbz` file:

```bash
$ ./scripts/import_mbz.sh content.mbz
```

The script will create the commit which includes the stages.

## Authoring environment

Before starting the authoring environment you must install and run Docker.
[get docker](https://docs.docker.com/get-docker/)

In order to start the authoring environment you can pass the `up` argument into the `authoring_env.sh` script. You can access the moodle instace at [http://localhost:8000](http://localhost:8000/) and login with `admin` as the username and password.

```bash
$ ./scripts/authoring_env.sh up
```

To stop the authoring environment use the `down` argument.

```bash
$ ./scripts/authoring_env.sh down
```

To stop the authoring environment and remove all database state, use the `destroy` argument. All courses will be removed from your local moodle environment.

```bash
$ ./scripts/authoring_env.sh destroy
```