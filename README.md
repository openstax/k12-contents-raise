# K12 Contents - RAISE

This repository contains course content and an authoring environment for the RAISE project.

## Content Authors

### Getting setup

Before starting the authoring environment you should install the following:
* [Docker](https://docs.docker.com/get-docker/)
* [VS Code](https://code.visualstudio.com/)

### Getting started

This authoring script is designed to help users start, stop, and configure an authoring environment. It provides a set of commands that allow users to create, modify, and delete content variants, and to start editing new rounds of content.

### How to Use the Script
To use the script, you need to run it from the command line and provide a valid command as the first argument. Here are the available commands:

- up: Starts the authoring environment.
- down: Stops the authoring environment.
- destroy: Stops the authoring environment and destroys all state.
- set-variant: Configures the content variant used for preview.
- reset-variant: Resets the variant used for preview to default.
- create-variant: Creates a variant HTML file for a page.
- start-editing: Initializes the environment for a new round of edits.

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

### Creating a variant

The create-variant command is used to create a variant HTML file for a page. To use this command, you need to provide the UUID and variant name arguments. For example, if you want to create a variant HTML file for a page with UUID "123" and variant name "interactive_study", you would run the following command:

```bash
$ ./scripts/authoring_env.sh create-variant interactive_study 123
```

### Setting a variant

The set-variant command is used to configure the content variant used for preview. To use this command, you need to provide the name of the variant as an argument. For example, if you want to set the variant to "interactive_study", you would run the following command:

```bash
$ ./scripts/authoring_env.sh set-variant interactive_study

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

