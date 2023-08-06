#!/bin/bash
set -e

TAG=fallenbreath/pterodactyl-installer:bullseye-17

docker build "$(pwd)" -t $TAG
if [ $# == 1 ] && [ "$1" == "-p" ]; then
  docker push $TAG
fi
