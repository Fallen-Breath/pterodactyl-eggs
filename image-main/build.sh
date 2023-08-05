#!/bin/bash
set -e

TAG=fallenbreath/pterodactyl-mc-mcdr:bullseye-17-2.10

docker build "$(pwd)" -t $TAG
if [ $# == 1 ] && [ "$1" == "-p" ]; then
  docker push $TAG
fi
