#!/bin/bash

set -e
cd /home/container

# Replace Startup Variables
STARTUP_CMD=$(echo "${STARTUP}" | sed -e 's/{{/${/g' -e 's/}}/}/g')
STARTUP_EXPANDED=$(echo "$STARTUP_CMD" | envsubst)
echo ":$(pwd)$ ${STARTUP_EXPANDED}"

# Run the Server
eval "${STARTUP_EXPANDED}"
