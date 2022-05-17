#!/usr/bin/env bash

set -e

if ! command -v extract-html-contents &> /dev/null; then
    echo "Please run this script in an environment with raise-mbtools set up"
    exit 1
fi

rm -rf mbz
cp -r mbz-dev mbz
remove-styles mbz
extract-html-contents mbz html
git add mbz html json
