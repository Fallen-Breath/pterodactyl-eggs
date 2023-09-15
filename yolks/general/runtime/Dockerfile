FROM debian:bullseye-slim

RUN sed -i.bak 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i.bak 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list \
    && apt-get update -y \
    && apt-get install -y ca-certificates curl git jq wget \
    && useradd -d /home/container -m container

USER container
ENV USER=container HOME=/home/container

WORKDIR /home/container
COPY ./entrypoint.sh /
CMD ["/bin/bash", "/entrypoint.sh"]
