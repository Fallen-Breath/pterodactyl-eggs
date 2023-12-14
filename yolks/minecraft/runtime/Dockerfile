ARG IMAGE_BASE=openjdk
ARG SYSTEM=bullseye
ARG JAVA_VERSION=17
FROM ${IMAGE_BASE}:${JAVA_VERSION}-jdk-${SYSTEM}

RUN apt-get update -y \
    && apt-get install -y curl ca-certificates openssl git tar sqlite3 fontconfig tzdata iproute2 \
    && apt-get install -y python3 python3-pip \
    && apt-get install -y gettext-base \
    && useradd -d /home/container -m container

COPY requirements.txt /requirements.txt
RUN python3 -m pip install -U pip \
    && pip3 install ruamel.yaml \
    && pip3 install -r /requirements.txt

ARG MCDR_REQUIREMENT=mcdreforged
RUN pip3 install -U ${MCDR_REQUIREMENT}

USER container
ENV USER=container HOME=/home/container

WORKDIR /home/container
COPY ./entrypoint.sh ./start_hook.py ./start_hook.yml /
CMD ["/bin/bash", "/entrypoint.sh"]
