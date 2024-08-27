#!/bin/env python3

import os
import requests
import locale
import traceback
import logging
import psycopg2
import time
import argparse
import sys
import datetime

from bs4 import BeautifulSoup  # pip install beautifulsoup4
import dateutil.parser

POSTGRES_USER = os.getenv('POSTGRES_USER', "root")
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', "postgres")
POSTGRES_HOST = os.getenv('POSTGRES_HOST', "localhost")
POSTGRES_PORT = os.getenv('POSTGRES_PORT', "5432")
POSTGRES_DATABASE = os.getenv('POSTGRES_DB', "postgres")


class VideoBuster():

    FILME_FETCH_URL = "https://www.videobuster.de/top-dvd-verleih-30-tage.php?pospage=1&search_title&tab_search_content=movies&view=9&wrapped=100#titlelist_head"

    def __init__(self, debug=False):
        self.debug = debug

    def fetch_movies(self) -> list:
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")
        html_text = BeautifulSoup(requests.get(VideoBuster.FILME_FETCH_URL).text, 'html.parser')

        database = list()
        tablerows = html_text.findAll('div', {'class':'detail-col'})
        for tablerow in tablerows:
            try:
                title_obj = tablerow.find('a')
                title_long_obj = tablerow.find('div', {'class': 'long-name'})
                movie_id = title_obj.attrs['href'].replace('/dvd-bluray-verleih/', '')
                title = title_obj.text
                title_long = title if title_long_obj is None else title_long_obj.text
                date = datetime.datetime.now().date()

                database.append({
                        'id': movie_id,
                        'title': title,
                        'longTitle': title_long,
                        'date': date,
                        })

            except:
                traceback.print_exc()

        return database


class TheMovieDb:

    def __init__(self, api_key, debug = False):
        self.logger = logging.getLogger('TheMovieDb')
        self.debug = debug
        self.api_key = api_key


    def rate_limit_protection(self):
        time.sleep(1)


    def fetch(self, url):
        headers = {
            "accept": "application/json"
        }
        self.rate_limit_protection()
        self.logger.debug("request url: %s", url)
        response = requests.get(url, headers=headers)
        return response.json()


    def fetch_discover_tv_full(self, page=1, air_date_gte="default"):
        default_air_date_gte = (datetime.datetime.now() - datetime.timedelta(days=31)).strftime("%Y-%m-%d")
        url = f"https://api.themoviedb.org/3/discover/tv?api_key={self.api_key}"
        url += "&air_date.gte={}".format(default_air_date_gte if air_date_gte == "default" else air_date_gte)
        url += "&include_adult=true"
        url += "&include_null_first_air_dates=false"
        url += "&language=de-DE"
        url += f"&page={page}"
        url += "&sort_by=popularity.desc"
        url += "&vote_average.gte=7"
        url += "&vote_count.gte=20"
        url += "&watch_region=DE"
        url += "&without_genres=16,37"
        url += "&with_watch_providers=8|9|337|350|2|30|29|10"
        return self.fetch(url)


    def fetch_discover_tv_relevant(self, page=1, air_date_gte="default"):
        result = self.fetch_discover_tv_full(page, air_date_gte)
        return [{'id': x['id'], 'name': x['name'], 'genre': x['genre_ids']} for x in result["results"]]


    def fetch_tv_full(self, series_id):
        url = f"https://api.themoviedb.org/3/tv/{series_id}?language=de-DE&api_key={self.api_key}"
        return self.fetch(url)


    def fetch_tv_relevant(self, series_id):
        data = self.fetch_tv_full(series_id)
        try:
            last_air_date = dateutil.parser.parse(data["last_air_date"])
            active = (datetime.datetime.now() - datetime.timedelta(days=7)) <= last_air_date
            result = {
                "id": data["id"],
                "name": data["name"],
                "in_production": data["in_production"],
                "active": data["next_episode_to_air"] is not None or active,
                "last_episode": data["last_episode_to_air"]["episode_number"],
                "last_season": data["last_episode_to_air"]["season_number"],
                "last_air_date": data["last_air_date"],
                "number_of_seasons": data["number_of_seasons"],
                "status": data["status"],
                "vote_average": data["vote_average"]
            }
        except Exception as ex:
            self.logger.exception(ex)
            self.logger.info("content: %s", str(data))
            result = {}

        return result


    def fetch_completed_series_seasons(self, search_pages = 3):
        result = []
        try:
            for page in range(1,search_pages+1):
                for item in self.fetch_discover_tv_relevant(page):
                    data = self.fetch_tv_relevant(item['id'])
                    if "active" in data and not data["active"]:
                        result.append({
                            "id": str(data["id"]) + "-" + str(data["last_season"]),
                            "title": data["name"],
                            "season": data["last_season"],
                            "date": data["last_air_date"]
                        })
        except:
            traceback.print_exc()

        return result


    def fetch_series_by_ids(self, ids: list):
        result = []
        try:
            self.logger.info("fetch ids %s", str(ids))
            for id in ids:
                data = self.fetch_tv_relevant(id)
                if "active" in data and not data["active"]:
                    result.append({
                        "id": str(data["id"]) + "-" + str(data["last_season"]),
                        "title": data["name"],
                        "season": data["last_season"],
                        "date": data["last_air_date"]
                    })
        except:
            traceback.print_exc()

        return result


class DebugDatabase():

    def __ini__(self):
        pass

    def commit(self):
        pass

    def insert_serie(self, data):
        print("insert", data)

    def insert_movie(self, data):
        print("insert", data)

    def insert_track(self, data):
        print("insert", data)

    def get_track_ids(self):
        return []


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
        self.__create_tracking_table_if_not_exists()


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
            STATE           TEXT    NOT NULL
            ); '''

        self.cursor.execute(create_serien_table_query)
        self.connection.commit()

    def __create_tracking_table_if_not_exists(self):
        create_track_table_query = '''CREATE TABLE IF NOT EXISTS TRACK
            (ID TEXT PRIMARY KEY    NOT NULL,
            TITLE           TEXT    NOT NULL,
            SEASON          INT     NOT NULL,
            DATE            DATE    NOT NULL,
            STATE           TEXT    NOT NULL
            ); '''

        self.cursor.execute(create_track_table_query)
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
        sql = f'''INSERT INTO SERIEN
            (ID,TITLE,SEASON,DATE,STATE)
            VALUES('{data['id']}','{data['title']}',{data['season']},'{data['date']}','New')
            ON CONFLICT DO NOTHING'''
        self.logger.debug('sql: %s', sql)
        self.cursor.execute(sql)

    def insert_track(self, data):
        data["title"] = data["title"].replace("'",'')
        sql = f'''INSERT INTO TRACK
            (ID,TITLE,SEASON,DATE,STATE)
            VALUES('{data['id']}','{data['title']}',{data['season']},'{data['date']}','New')
            ON CONFLICT DO NOTHING'''
        self.logger.debug('sql: %s', sql)
        self.cursor.execute(sql)

    def get_track_ids(self):
        ids = []
        try:
            self.cursor.execute("SELECT ID FROM TRACKID")
            ids = list(map(lambda x: x[0], self.cursor.fetchall()))
        except:
            traceback.print_exc()
        return ids

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
    parser.add_argument('--skip-track', action='store_true', help="skip fetch track infos")
    args = parser.parse_args()

    db = DebugDatabase() if args.debug else Database()


    the_movie_db_api_key = os.getenv('THE_MOVIE_DB_API_KEY', "")
    if the_movie_db_api_key == "":
        print("env var THE_MOVIE_DB_API_KEY missing")
        time.sleep(1)
        sys.exit(1)

    video_buster = VideoBuster(args.debug)
    if not args.skip_movies:
        logger.info("fetch new movies")
        movies = video_buster.fetch_movies()
        for movie in movies:
            try:
                db.insert_movie(movie)
            except Exception as ex:
                logger.exception(ex)

    the_movide_db = TheMovieDb(the_movie_db_api_key, args.debug)
    if not args.skip_serien:
        logger.info("fetch new serien")
        serien = the_movide_db.fetch_completed_series_seasons()
        for serie in serien:
            try:
                db.insert_serie(serie)
            except Exception as ex:
                logger.exception(ex)

    if not args.skip_track:
        logger.info("fetch new track infos")
        serien = the_movide_db.fetch_series_by_ids(db.get_track_ids())
        for serie in serien:
            try:
                db.insert_track(serie)
            except Exception as ex:
                logger.exception(ex)

    db.commit()
    logger.info("movies and serien data crawler completed")
