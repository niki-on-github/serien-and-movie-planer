#!/bin/env python3

import os
import requests
import locale
import traceback
import logging
import psycopg2
import argparse

from bs4 import BeautifulSoup  # pip install beautifulsoup4
from datetime import datetime, timedelta
import dateutil.parser

SERIEN_URL = "https://www.serienjunkies.de/docs/serienplaner.html"
FILME_URL = "https://www.videobuster.de/top-dvd-verleih-30-tage.php?pospage=1&search_title&tab_search_content=movies&view=9&wrapped=100#titlelist_head"
POSTGRES_USER = os.getenv('POSTGRES_USER', "root")
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', "postgres")
POSTGRES_HOST = os.getenv('POSTGRES_HOST', "localhost")
POSTGRES_PORT = os.getenv('POSTGRES_PORT', "5432")
POSTGRES_DATABASE = os.getenv('POSTGRES_DB', "postgres")


def debug_print(title, objs):
    if not isinstance(objs, list):
        objs = [objs]
    for idx, obj in enumerate(objs):
        debug_txt = str(obj).replace("\n", " ")
        while "  " in debug_txt:
            debug_txt = debug_txt.replace("  ", " ")
        print(title, idx, ":", debug_txt)


def fetch_serien(debug = False) -> list:
    logger = logging.getLogger("serien")
    locale.setlocale(locale.LC_TIME, ("de_DE", "UTF8"))
    html_text = BeautifulSoup(requests.get(SERIEN_URL).text, 'html.parser')

    database = list()
    tablerows = html_text.findAll('div', {'class':'tablerow'})
    for tablerow in tablerows:
        if debug:
            print("")
            print("="*80)
            debug_print("tablerow", tablerow)
        try:
            tablecels = tablerow.findAll('div', {'class':'tablecell'})
            if debug:
                debug_print("tablecels", tablecels)
            if len(tablecels) != 3:
                continue
            title = tablecels[1].findAll('p')

            if len(title) == 0:
                continue

            title = title[0].text.strip()
            if debug:
                print("title:", title)
            season = tablecels[1].findAll('a')[0].attrs['href'].split("/")[-1].replace(".html", "").replace("season", "").encode("ascii", "ignore").decode()
            if season == "":
                logger.warning("Season is empty for %s", title)
                season = "0"

            if not season.isnumeric():
                logger.warning("Season '%s' is not an Season number for %s", season, title)
                season = "0"

            if debug:
                print("season:", season)
            date = tablecels[1].findAll('div')[0].text.replace("Serienstart", "").strip()

            if "Morgen" in date:
                date = (datetime.now() + timedelta(1)).date()
            elif "Heute" in date:
                date = datetime.now().date()
            elif "Übermorgen" in date:
                date = (datetime.now() + timedelta(2)).date()
            else:
                date = date.split("  ", 2)[0]
                for x in ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]:
                    date = date.replace(x, "")
                for idx, x in enumerate(["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "Oktober", "November", "Dezember"]):
                    date = date.replace(x, str(idx+1))
                date = date.replace(",", "")
                date = date.strip()
                if debug:
                    print("date:", date)
                date = dateutil.parser.parse(date)

            try:
                sender = tablecels[2].findAll('a')[0].attrs['href'].replace("/sender/", "").replace("/", "")
            except:
                sender = "unknown"

            if debug:
                print("sender:", sender)

            database.append({
                    'title': title.encode("ascii", "ignore").decode(),
                    'season': season.encode("ascii", "ignore").decode(),
                    'date': date,
                    'sender': sender.encode("ascii", "ignore").decode()
                    })
        except:
            try: debug_print("tablerow", tablerow)
            except: pass
            traceback.print_exc()

    return database


def fetch_movies(debug = False) -> list:
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


class DebugDatabase():

    def __ini__(self):
        pass

    def commit(self):
        pass

    def insert_serie(self, data):
        print("insert", data)

    def insert_movie(self, data):
        print("insert", data)


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

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help="use debug mode")
    parser.add_argument('--skip-movies', action='store_true', help="skip fetch movies")
    parser.add_argument('--skip-serien', action='store_true', help="skip fetch serien")
    args = parser.parse_args()

    db = DebugDatabase() if args.debug else Database()

    if not args.skip_movies:
        logger.info("fetch new movies")
        movies = fetch_movies(args.debug)
        for movie in movies:
            db.insert_movie(movie)

    if not args.skip_serien:
        logger.info("fetch new serien")
        serien = fetch_serien(args.debug)
        for serie in serien:
            db.insert_serie(serie)

    db.commit()
    logger.info("movies and serien data crawler completed")
