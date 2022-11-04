import psycopg2
import json
import os
import sys
import logging

POSTGRES_USER = "root"
POSTGRES_PASSWORD = "Geheim"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_DATABASE = "postgres"

with open('./database.json', 'r') as fd:
    DATA = json.load(fd)

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=os.getenv('LOG_LEVEL', "DEBUG"),
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(stream=sys.stdout)
    ]
)

connection = psycopg2.connect(
    user = POSTGRES_USER,
    password = POSTGRES_PASSWORD,
    host = POSTGRES_HOST,
    port = POSTGRES_PORT,
    database = POSTGRES_DATABASE
)

cursor = connection.cursor()

create_movie_table_query = '''CREATE TABLE IF NOT EXISTS MOVIES
    (ID INT PRIMARY KEY     NOT NULL,
    TITLE           TEXT    NOT NULL,
    LONG_TITLE      TEXT    NOT NULL,
    DATE            DATE    NOT NULL,
    STATE           TEXT    NOT NULL
    ); '''

cursor.execute(create_movie_table_query)
connection.commit()

create_serien_table_query = '''CREATE TABLE IF NOT EXISTS SERIEN
    (ID TEXT PRIMARY KEY    NOT NULL,
    TITLE           TEXT    NOT NULL,
    SEASON          INT     NOT NULL,
    DATE            DATE    NOT NULL,
    SENDER          TEXT    NOT NULL,
    STATE           TEXT    NOT NULL
    ); '''

cursor.execute(create_serien_table_query)
connection.commit()

for k in DATA["movies"]:
    item = DATA["movies"][k]
    item['title'] = item['title'].replace("'",'')
    item['longTitle'] = item['longTitle'].replace("'",'')
    sql = f'''INSERT INTO MOVIES
        (ID,TITLE,LONG_TITLE,DATE,STATE)
        VALUES({k.split('/')[0]},'{item['title']}','{item['longTitle']}','{item['date']}', 'New')
        ON CONFLICT DO NOTHING'''
    logger.debug('sql: %s', sql)
    cursor.execute(sql)

for k in DATA["serien"]:
    for season in DATA["serien"][k]:
        item = DATA["serien"][k][season]
        title = k.replace("'",'')
        table_id = title + ' - Season ' + season
        sql = f'''INSERT INTO SERIEN
            (ID,TITLE,SEASON,DATE,SENDER,STATE)
            VALUES('{table_id}','{title}',{season},'{item['date']}','{item['sender']}','New')
            ON CONFLICT DO NOTHING'''
        logger.debug('sql: %s', sql)
        cursor.execute(sql)

connection.commit()
cursor.close()
connection.close()
