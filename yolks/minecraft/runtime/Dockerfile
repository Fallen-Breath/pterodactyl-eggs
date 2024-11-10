ARG MCDR_VERSION=latest
ARG JAVA_VERSION=21
FROM mcdreforged/mcdreforged-temurin:${MCDR_VERSION}-slim-jdk${JAVA_VERSION}-extra

RUN <<EOT
set -eux
apt-get update -y
apt-get install -y curl ca-certificates openssl git tar sqlite3 fontconfig tzdata iproute2
apt-get install -y gettext-base
useradd -d /home/container -m container
EOT

USER container
ENV USER=container HOME=/home/container

WORKDIR /home/container
COPY ./entrypoint.sh ./start_hook.py ./start_hook.yml /
CMD ["/bin/bash", "/entrypoint.sh"]
