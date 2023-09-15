#!/bin/bash

set -e

for SYS in "debian" "alpine"; do
  TAG="fallenbreath/pterodactyl-yolks:general-installer-${SYS}"

  docker build "$(pwd)" -t "$TAG" -f "Dockerfile-${SYS}"
  if [ $# == 1 ] && [ "$1" == "-p" ]; then
    docker push "$TAG"
  fi
done