import os

import dj_database_url
import MySQLdb as mdb


def get_db_info_from_env():
    database_url = os.environ.get("DATABASE_URL")
    return dj_database_url.parse(database_url)


def connect_to_database(db_info):
    con = mdb.connect(db_info["HOST"], db_info['USER'], db_info["PASSWORD"], db_info["NAME"])
    cur = con.cursor(mdb.cursors.DictCursor)
    return con, cur
