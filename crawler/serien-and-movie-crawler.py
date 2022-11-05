#!/bin/env python3

import os
import requests
import locale
import traceback
import logging
import psycopg2

from bs4 import BeautifulSoup  # pip install beautifulsoup4
from datetime import datetime, timedelta

SERIEN_URL = "https://www.serienjunkies.de/docs/serienplaner.html"
FILME_URL = "https://www.videobuster.de/top-dvd-verleih-30-tage.php?pospage=1&search_title&tab_search_content=movies&view=9&wrapped=100#titlelist_head"
POSTGRES_USER = os.getenv('POSTGRES_USER', "root")
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', "Geheim")
POSTGRES_HOST = os.getenv('POSTGRES_HOST', "localhost")
POSTGRES_PORT = os.getenv('POSTGRES_PORT', "5432")
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE', "postgres")


def fetch_serien() -> list:
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    html_text = BeautifulSoup(requests.get(SERIEN_URL).text, 'html.parser')

    database = list()
    tablerows = html_text.findAll('div', {'class':'tablerow'})
    for tablerow in tablerows:
        try:
            tablecels = tablerow.findAll('div', {'class':'tdva'})
            if len(tablecels) != 2:
                continue
            title = tablecels[0].findAll('div')[0].text.strip().split("Staffel")
            season = title[1].strip() if len(title) > 1 else "0"
            title = title[0].strip()
            date = tablecels[0].findAll('div')[1].text.strip()
            if "Morgen" in date:
                date = (datetime.now() + timedelta(1)).date()
            elif "Heute" in date:
                date = datetime.now().date()
            else:
                year = int(datetime.now().date().strftime("%Y"))
                date = date.split(str(year), 2)
                if len(date) == 2:
                    date = datetime.strptime(date[0] + str(year), '%A, %d.%B %Y').date()
                else:
                    date = date.split(str(year-1), 2)
                    if len(date) == 2:
                        date = datetime.strptime(date[0] + str(year-1), '%A, %d.%B %Y').date()
                    else:
                        date = date.split(str(year+1), 2)
                        if len(date) == 2:
                            date = datetime.strptime(date[0] + str(year+1), '%A, %d.%B %Y').date()
                        else:
                            date = "?"
            try:
                sender = tablecels[1].img['title'].strip()
            except:
                sender = tablecels[1].a['title'].strip()

            database.append({
                    'title': title.encode("ascii", "ignore").decode(),
                    'season': season.encode("ascii", "ignore").decode(),
                    'date': date,
                    'sender': sender.encode("ascii", "ignore").decode()
                    })
        except:
            traceback.print_exc()

    return database


def fetch_movies() -> list:
    locale.setlocale(locale.LC_TIME, "de_DE.utf8")
    html_text = BeautifulSoup(requests.get(FILME_URL).text, 'html.parser')

    database = list()
    tablerows = html_text.findAll('div', {'class':'detail-col'})
    for tablerow in tablerows:
        try:
            title_obj = tablerow.find('a')
            title_long_obj = tablerow.find('div', {'class': 'long-name'})
            movie_id = title_obj.attrs['href'].replace('/dvd-bluray-verleih/', '')
            title = title_obj.text
            title_long = title if title_long_obj is None else title_long_obj.text
            date = datetime.now().date()

            database.append({
                    'id': movie_id,
                    'title': title,
                    'longTitle': title_long,
                    'date': date,
                    })

        except:
            traceback.print_exc()

    return database


class Database:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.connection = psycopg2.connect(
            user = POSTGRES_USER,
            password = POSTGRES_PASSWORD,
            host = POSTGRES_HOST,
            port = POSTGRES_PORT,
            database = POSTGRES_DATABASE
        )

        self.cursor = self.connection.cursor()

        self.__create_movie_table_if_not_exists()
        self.__create_serien_table_if_not_exists()


    def __del__(self):
        try:
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
        except:
            pass


    def __create_movie_table_if_not_exists(self):
        create_movie_table_query = '''CREATE TABLE IF NOT EXISTS MOVIES
            (ID INT PRIMARY KEY     NOT NULL,
            TITLE           TEXT    NOT NULL,
            LONG_TITLE      TEXT    NOT NULL,
            DATE            DATE    NOT NULL,
            STATE           TEXT    NOT NULL
            ); '''

        self.cursor.execute(create_movie_table_query)
        self.connection.commit()


    def __create_serien_table_if_not_exists(self):
        create_serien_table_query = '''CREATE TABLE IF NOT EXISTS SERIEN
            (ID TEXT PRIMARY KEY    NOT NULL,
            TITLE           TEXT    NOT NULL,
            SEASON          INT     NOT NULL,
            DATE            DATE    NOT NULL,
            SENDER          TEXT    NOT NULL,
            STATE           TEXT    NOT NULL
            ); '''

        self.cursor.execute(create_serien_table_query)
        self.connection.commit()


    def insert_movie(self, data):
        data['title'] = data['title'].replace("'",'')
        data['longTitle'] = data['longTitle'].replace("'",'')
        data['id'] = data['id'].split('/')[0]
        sql = f'''INSERT INTO MOVIES
                (ID,TITLE,LONG_TITLE,DATE,STATE)
                VALUES({data['id']},'{data['title']}','{data['longTitle']}','{data['date']}', 'New')
                ON CONFLICT DO NOTHING'''
        self.logger.debug('sql: %s', sql)
        self.cursor.execute(sql)


    def insert_serie(self, data):
        data["title"] = data["title"].replace("'",'')
        table_id = data["title"] + ' - Season ' + str(data["season"])
        sql = f'''INSERT INTO SERIEN
            (ID,TITLE,SEASON,DATE,SENDER,STATE)
            VALUES('{table_id}','{data['title']}',{data['season']},'{data['date']}','{data['sender']}','New')
            ON CONFLICT DO NOTHING'''
        self.logger.debug('sql: %s', sql)
        self.cursor.execute(sql)


    def commit(self):
        self.connection.commit()


def setup_logging():
    logging.basicConfig(
        level=os.getenv('LOG_LEVEL', "INFO"),
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler()
        ]
    )


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    setup_logging()

    db = Database()

    logger.info("fetch new movies")
    movies = fetch_movies()
    for movie in movies:
        db.insert_movie(movie)

    logger.info("fetch new serien")
    serien = fetch_serien()
    for serie in serien:
        db.insert_serie(serie)

    db.commit()
    logger.info("movies and serien data crawler completed")
