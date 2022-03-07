FROM python:3.8-slim

COPY config.json ~/.config/telegram-archive-bot/config.json

RUN rm /bin/sh && \
    ln -s /bin/bash /bin/sh && \
    apt-get update && \
    apt-get install -y gcc htop && \
    pip3 install --upgrade pip && \
    pip3 install virtualenv python-telegram-bot logzero && \
    virtualenv -p python3 venv
RUN source venv/bin/activate