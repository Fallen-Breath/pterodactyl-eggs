#!/bin/bash

set -e

cd /home/container

# Output Current Java Version
java -version

# Output Current Python Version
python3 -V

# Replace Startup Variables
STARTUP_CMD=$(echo "${STARTUP}" | sed -e 's/{{/${/g' -e 's/}}/}/g')
STARTUP_EXPANDED=$(envsubst <<< "$STARTUP_CMD")
echo ":$(pwd)$ ${STARTUP_EXPANDED}"

# Run the Server
eval "${STARTUP_EXPANDED}"
