from peewee import *

import config

db = SqliteDatabase(config.db)


class User(Model):
    user_id = TextField(unique=True)
    chat_id = TextField(unique=True)
    config = TextField()
    data = TextField(null=True)

    class Meta:
        database = db


db.connect()
db.create_tables([User])
