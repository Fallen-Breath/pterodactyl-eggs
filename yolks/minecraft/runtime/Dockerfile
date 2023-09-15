ARG SYSTEM=bullseye
ARG JAVA_VERSION=17
FROM openjdk:${JAVA_VERSION}-jdk-${SYSTEM}

RUN sed -i.bak 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i.bak 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list \
    && apt-get update -y \
    && apt-get install -y curl ca-certificates openssl git tar sqlite3 fontconfig tzdata iproute2 \
    && apt-get install -y python3 python3-pip \
    && apt-get install -y gettext-base \
    && useradd -d /home/container -m container

COPY requirements.txt /requirements.txt
RUN python3 -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip3 install ruamel.yaml -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip3 install -r /requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

ARG MCDR_REQUIREMENT="mcdreforged"
RUN pip3 install -U ${MCDR_REQUIREMENT} -i https://pypi.tuna.tsinghua.edu.cn/simple

USER container
ENV USER=container HOME=/home/container

WORKDIR /home/container
COPY ./entrypoint.sh ./start_hook.py ./start_hook.yml /
CMD ["/bin/bash", "/entrypoint.sh"]
