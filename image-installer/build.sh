#!/bin/bash

TAG=fallenbreath/pterodactyl-installer:debian-11-slim

docker build "$(pwd)" -t $TAG
if [ $# == 1 ] && [ "$1" == "-p" ]; then
  docker push $TAG
fi
