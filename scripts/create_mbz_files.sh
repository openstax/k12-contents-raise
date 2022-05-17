#!/usr/bin/env bash

set -e

MBZ_DEV_OUTPUT="raise-dev-$(git rev-parse --short HEAD).mbz"
MBZ_OUTPUT="raise-$(git rev-parse --short HEAD).mbz"

tar -C ./mbz-dev -cvzf "$MBZ_DEV_OUTPUT" .
tar -C ./mbz -cvzf "$MBZ_OUTPUT" .
