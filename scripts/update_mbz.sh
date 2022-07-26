#!/usr/bin/env bash

set -e

if ! command -v extract-html-contents &> /dev/null; then
    echo "Please run this script in an environment with raise-mbtools set up"
    exit 1
fi

# Copy mbz-dev to mbz
rm -rf mbz
cp -r mbz-dev mbz
git add mbz
git commit -m "Move mbz-dev to mbz tree"
# Remove styles
remove-styles mbz
git add mbz
git commit -m "Run mbtools remove-styles"
# Extract HTML
extract-html-contents mbz html
git add mbz html
git commit -m "Run mbtools extract-html"
html-to-json html json
git add json
git commit -m "Run mbtools html-to-json"
generate-mbz-toc mbz toc.md
git add toc.md
git commit -m "Update mbz table of contents"
