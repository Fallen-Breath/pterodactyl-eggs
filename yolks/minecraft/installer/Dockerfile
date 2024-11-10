ARG JAVA_VERSION=21
FROM eclipse-temurin:${JAVA_VERSION}

RUN <<EOT
set -eux
apt-get update -y
apt-get install -y python3 python3-pip
pip3 install requests ruamel.yaml --break-system-packages -i https://pypi.tuna.tsinghua.edu.cn/simple
EOT

COPY ./minecraft_installer.py /
