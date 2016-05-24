# -*- coding: utf-8 -*-
import sys

try:
    import html2text
except ImportError as exc:
    print('Error: failed to import module. ({}). \nInstall missing modules'
          ' using "sudo pip install -r requirements.txt"'.format(exc))
    sys.exit(0)


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
        self.LastTitle = ''
        self.NewTitle = ''
        self.ArticleUrl = ''
        self.Description = ''

    def jointext(self):
        text = ''
        h = html2text.HTML2Text()
        h.ignore_links = True
        self.Description = h.handle(self.Description)
        if self.ShowName is True:
            text += "_" + self.Name + '_\n'
        if self.ShowTitle is True:
            text += '*' + self.NewTitle + '*\n'
        if self.ShowDescription is True:
            text += self.Description + '\n'
        if self.ShowUrl is True:
            text += self.ArticleUrl
        return text
