#!/bin/bash
set -e

for SYS in "bullseye" "slim-bullseye"; do
  for JAVA in 8 17; do
    for MCDR in "2.10" "latest"; do
      if [ "$MCDR" == "latest" ]; then
        MCDR_REQUIREMENT="mcdreforged"
      else
        MCDR_REQUIREMENT="mcdreforged~=${MCDR}"
      fi
      TAG="fallenbreath/pterodactyl-mc-mcdr:${SYS}-${JAVA}-${MCDR}"
      echo "======== System: $SYS, Java: $JAVA, MCDR: $MCDR, Tag: $TAG ========"

      docker build "$(pwd)" \
        --build-arg SYSTEM=${SYS} \
        --build-arg JAVA_VERSION=${JAVA} \
        --build-arg MCDR_REQUIREMENT=${MCDR_REQUIREMENT} \
        -t "$TAG"

      if [ $# == 1 ] && [ "$1" == "-p" ]; then
        docker push $TAG
      fi
    done
  done
done
