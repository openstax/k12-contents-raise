#!/usr/bin/env bash

set -e

MBZ_OUTPUT="raise-$(git rev-parse --short HEAD).mbz"

tar -C ./mbz -cvzf "$MBZ_OUTPUT" .
