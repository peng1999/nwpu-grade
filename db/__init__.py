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
    config = BlobField(null=True)
    data = BlobField(null=True)
    monitor_running = BooleanField(default=False)


db.connect()
db.create_tables([User])
