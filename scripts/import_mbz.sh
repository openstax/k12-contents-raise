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

rm -rf mbz
mkdir mbz
tar -C mbz -xvzf "$INPUT_MBZ"
git add mbz
git commit -m "Import mbz tree"
