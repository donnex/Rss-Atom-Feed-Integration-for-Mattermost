# -*- coding: utf-8 -*-
import sys
from datetime import datetime

from peewee import CharField, DateTimeField, Model, TextField
from playhouse.sqlite_ext import SqliteExtDatabase

db = SqliteExtDatabase('db/rss_atom_mattermost.db')
db.connect()

try:
    import html2text
except ImportError as exc:
    print('Error: failed to import module. ({}). \nInstall missing modules'
          ' using "sudo pip install -r requirements.txt"'.format(exc))
    sys.exit(1)


class RssFeed(object):
    def __init__(self, name, url, iconurl, user, channel, showname, showtitle,
                 showdescription, showurl):
        self.Name = name
        self.Url = url
        self.Iconurl = iconurl
        self.User = user
        self.Channel = channel
        self.ShowName = showname
        self.ShowTitle = showtitle
        self.ShowDescription = showdescription
        self.ShowUrl = showurl


class RssFeedItem(Model):
    title = CharField()
    url = CharField()
    rss_feed = CharField()

    description = TextField(default='')

    created_date = DateTimeField(default=datetime.now)

    class Meta:
        database = db

    def jointext(self, rss_feed):
        text = ''
        h = html2text.HTML2Text()
        h.ignore_links = True
        description = h.handle(self.description)

        if rss_feed.ShowName is True:
            text += '_' + rss_feed.Name + '_\n'
        if rss_feed.ShowTitle is True:
            text += '*' + self.title + '*\n'
        if rss_feed.ShowDescription is True:
            text += description + '\n'
        if rss_feed.ShowUrl is True:
            text += self.url

        return text

db.create_tables([RssFeedItem], safe=True)
