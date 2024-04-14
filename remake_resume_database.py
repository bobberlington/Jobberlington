import flask_sqlalchemy
import sqlalchemy
import sqlite3
from datetime import datetime
from credentials import resume

con = sqlite3.connect("jobs.db")
cur = con.cursor()
# cur.execute("""CREATE TABLE resume(
#                 id integer PRIMARY KEY AUTOINCREMENT,
#                 date datetime,
#                 resume varchar
#            );""")
cur.execute(f"INSERT INTO resume (date, resume) VALUES (?, ?);", (datetime.now(), resume))
con.commit()


