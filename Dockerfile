FROM python:3.10-slim

COPY . /DramaBot
WORKDIR /DramaBot

RUN chmod +x healthcheck.sh

RUN pip install -r requirements.txt
CMD python bot.py
