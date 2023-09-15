#!/bin/bash

set -e
TAG="fallenbreath/pterodactyl-yolks:general-runtime-debian"

docker build "$(pwd)" -t "$TAG"
if [ $# == 1 ] && [ "$1" == "-p" ]; then
  docker push $TAG
fi
