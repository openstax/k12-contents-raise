# K12 Contents - RAISE

This repository contains course content and an authoring environment for the RAISE project.

## Content Authors

### Getting setup

Before starting the authoring environment you should install the following:
* [Docker](https://docs.docker.com/get-docker/)
* [VS Code](https://code.visualstudio.com/)

### Getting started

To launch an environment, you can run the following command passing a unique branch name in place of `REPLACEME` to create locally:

```bash
$ ./scripts/authoring_env.sh start-editing REPLACEME
```

You can access the moodle instace at [http://localhost:8000](http://localhost:8000/) and login with `admin` as the username and password. The command will automatically deploy a course into the Moodle instance with the latest `mbz` from this repository.

**NOTE:** The same command should be used when creating a new PR to ensure you are at a known state.

### Resuming the environment

In order to start the authoring environment after a system reboot or similar, you can pass the `up` argument into the `authoring_env.sh` script.

```bash
$ ./scripts/authoring_env.sh up
```

### Stopping the environment

To stop the authoring environment use the `down` argument.

```bash
$ ./scripts/authoring_env.sh down
```

## Developers

### Generating MBZ files for import into Moodle

In order to import content from this repository into Moodle, you can run the following script:

```bash
$ ./scripts/create_mbz_files.sh
```

The script will generate files with a git short ref in the filename so it's clear what content version was used to generate the file.

### Import `mbz` content

The content in the `mbz` directory of this repo can be updated given an input `.mbz` file:

```bash
$ ./scripts/import_mbz.sh content.mbz
```

The script will create the commit which includes the stages.

