FROM python:3.11-slim

ENV LC_ALL de_DE.UTF-8
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE.UTF-8

RUN apt-get update \
    && apt-get install -y locales locales-all \
    && pip install beautifulsoup4 python-dateutil requests psycopg2-binary --no-cache-dir \
    && mkdir -p /app \
    && rm -rf /var/lib/apt/lists/*

ADD ./entrypoint.sh /app
ADD ./serien-and-movie-crawler.py /app

RUN chmod +x /app/entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
