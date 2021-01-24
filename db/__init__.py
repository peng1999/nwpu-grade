from peewee import *

import config

db = SqliteDatabase(config.db)


class AppModel(Model):
    class Meta:
        database = db


class User(AppModel):
    user_id = TextField(primary_key=True)
    chat_id = TextField(null=True)
    university = TextField(null=True)
    config = TextField(null=True)
    data = TextField(null=True)


db.connect()
db.create_tables([User])
