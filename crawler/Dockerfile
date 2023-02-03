FROM python:3.10

RUN apt-get update
RUN apt-get install -y locales locales-all

ENV LC_ALL de_DE.UTF-8
ENV LANG de_DE.UTF-8
ENV LANGUAGE de_DE.UTF-8

RUN pip install \
    beautifulsoup4 \
    python-dateutil \
    requests \
    psycopg2

RUN mkdir -p /app

ADD ./entrypoint.sh /app
ADD ./serien-and-movie-crawler.py /app

RUN chmod +x /app/entrypoint.sh

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]
