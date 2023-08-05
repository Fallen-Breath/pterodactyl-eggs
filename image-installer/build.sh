#!/bin/bash
set -e

TAG=fallenbreath/pterodactyl-installer:python-slim-bullseye

docker build "$(pwd)" -t $TAG
if [ $# == 1 ] && [ "$1" == "-p" ]; then
  docker push $TAG
fi
