import datetime
from peewee import (SqliteDatabase, Model, DateTimeField, CharField, TextField, ForeignKeyField)

database = SqliteDatabase(None)


class BaseModel(Model):
    class Meta:
        database = database


class Page(BaseModel):
    url = CharField(unique=True)
    content = TextField()
    first_visited = DateTimeField(default=datetime.datetime.utcnow)  # actually means "first_seen"
    last_visited = DateTimeField(default=datetime.datetime.utcnow)


class Link(BaseModel):
    from_page = ForeignKeyField(Page, related_name='links_from')
    to_page = ForeignKeyField(Page, related_name='links_to')

    class Meta:
        indexes = (
            (('from_page', 'to_page'), True),  # peewee's unique together
        )


def initialize(db_name):
    database.init(db_name)
    Page.create_table(fail_silently=True)
    Link.create_table(fail_silently=True)
