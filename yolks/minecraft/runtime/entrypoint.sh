#!/bin/bash

set -e

cd /home/container

# Output Current Java Version
java -version

# Output Current Python Version
python3 -V

# Run the start-hook
python3 /start_hook.py

# Replace Startup Variables
STARTUP_CMD=$(echo "${STARTUP}" | sed -e 's/{{/${/g' -e 's/}}/}/g')
STARTUP_EXPANDED=$(echo "$STARTUP_CMD" | envsubst)
echo ":$(pwd)$ ${STARTUP_EXPANDED}"

# Run the Server
eval "${STARTUP_EXPANDED}"
