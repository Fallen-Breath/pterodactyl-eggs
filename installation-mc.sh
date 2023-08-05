#!/bin/bash
# Vanilla MC + MCDReforged Installation Script
#
# Server Files: /mnt/server

mkdir -p /mnt/server
cd /mnt/server

set -e

echo "=============================== Install Installation Requirements ==============================="

export DEBIAN_FRONTEND=noninteractive
sed -i.bak 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
sed -i.bak 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list
apt-get update
apt-get install -y curl jq

echo "=============================== Set INSTALLATION_MARK for pre_start hook ==============================="

echo "touching INSTALLATION_MARK"
touch INSTALLATION_MARK

echo "=============================== Initialize Vanilla Minecraft ==============================="

mkdir -p server
cd server

LATEST_VERSION=$(curl -s https://launchermeta.mojang.com/mc/game/version_manifest.json | jq -r '.latest.release')
LATEST_SNAPSHOT_VERSION=$(curl -s https://launchermeta.mojang.com/mc/game/version_manifest.json | jq -r '.latest.snapshot')

echo -e "latest version is $LATEST_VERSION"
echo -e "latest snapshot is $LATEST_SNAPSHOT_VERSION"

if [ -z "$VANILLA_VERSION" ] || [ "$VANILLA_VERSION" == "latest" ]; then
  MANIFEST_URL=$(curl -sSL https://launchermeta.mojang.com/mc/game/version_manifest.json | jq --arg VERSION "$LATEST_VERSION" -r '.versions | .[] | select(.id== $VERSION )|.url')
elif [ "$VANILLA_VERSION" == "snapshot" ]; then
  MANIFEST_URL=$(curl -sSL https://launchermeta.mojang.com/mc/game/version_manifest.json | jq --arg VERSION "$LATEST_SNAPSHOT_VERSION" -r '.versions | .[] | select(.id== $VERSION )|.url')
else
  MANIFEST_URL=$(curl -sSL https://launchermeta.mojang.com/mc/game/version_manifest.json | jq --arg VERSION "$VANILLA_VERSION" -r '.versions | .[] | select(.id== $VERSION )|.url')
fi

DOWNLOAD_URL=$(curl -s "${MANIFEST_URL}" | jq .downloads.server | jq -r '. | .url')

CMD="curl -s --progress-bar -o ${SERVER_JARFILE} $DOWNLOAD_URL"
echo -e "running: $CMD"
eval "$CMD"

echo "=============================== Done ==============================="

echo -e "Install Script Complete!"
