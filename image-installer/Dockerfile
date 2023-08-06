FROM openjdk:17-jdk-slim-bullseye

RUN sed -i.bak 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list \
    && sed -i.bak 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list \
    && apt-get update -y \
    && apt-get install -y python3 python3-pip \
    && python3 -m pip install -U pip -i https://pypi.tuna.tsinghua.edu.cn/simple \
    && pip3 install requests ruamel.yaml -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY ./minecraft_installer.py /
