#!/usr/bin/env bash

set -e

INPUT_MBZ=$1

if [ -z "$INPUT_MBZ" ]; then
    echo "Provide input file argument"
    exit 1
fi

if [ ! -e "$INPUT_MBZ" ]; then
    echo "Input file '${INPUT_MBZ}' does not exist!"
    exit 1
fi

rm -rf mbz-dev
mkdir mbz-dev
tar -C mbz-dev -xvzf "$INPUT_MBZ"
git add mbz-dev
