#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import sys
import logging
import settings
import ssl
try:
    import feedparser
    import requests
except ImportError as exc:
    print('Error: failed to import module ({}). \nInstall missing modules'
          ' using "sudo pip install -r requirements.txt"'.format(exc))
    sys.exit(1)

from rssfeed import RssFeedItem

mattermost_webhook_url = settings.mattermost_webhook_url
delay_between_pulls = settings.delay_between_pulls
verify_cert = settings.verify_cert
silent_mode = settings.silent_mode
feeds = settings.feeds

if (not verify_cert) and hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


def post_text(text, username, channel, iconurl):
    """Mattermost POST method.

    Posts text to the Mattermost incoming webhook.
    """

    data = {}
    data['text'] = text
    if len(username) > 0:
        data['username'] = username
    if len(channel) > 0:
        data['channel'] = channel
    if len(iconurl) > 0:
        data['icon_url'] = iconurl

    headers = {'Content-Type': 'application/json'}

    # Mattermost POST request
    try:
        r = requests.post(mattermost_webhook_url, headers=headers,
                          data=json.dumps(data), verify=verify_cert)
    except requests.exceptions.RequestException as e:
        logging.error('Mattermost POST failed (%s)', e)
    else:
        if r.status_code is not requests.codes.ok:
            logging.debug('Encountered error posting to Mattermost URL %s, '
                          'status=%d, response_body=%s' %
                          (mattermost_webhook_url, r.status_code, r.json()))


if __name__ == '__main__':
    logging_format = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG,
                        format=logging_format)
    logging.getLogger('peewee').setLevel(logging.WARNING)

    if len(mattermost_webhook_url) == 0:
        print('mattermost_webhook_url must be configured. Please see '
              'instructions in README.md')
        sys.exit(1)

    while True:
        for feed in feeds:
            try:
                d = feedparser.parse(feed.Url)
                if not d['feed']:
                    logging.error('Could not fetch %s', feed.Url)
                    continue

                # Loop feed items
                for feed_item in d['entries']:
                    rss_feed_item, created = RssFeedItem.get_or_create(
                        title=feed_item['title'], url=feed_item['link'],
                        rss_feed=feed.Url)

                    # Announce if new / created
                    if created:
                        # Set and save description
                        rss_feed_item.description = feed_item['description']
                        rss_feed_item.save()

                        text_content = rss_feed_item.jointext(feed)

                        if not silent_mode:
                            logging.debug('Feed url: ' + rss_feed_item.url)
                            logging.debug('Title: ' + rss_feed_item.title)
                            logging.debug('Link: ' + rss_feed_item.url)
                            logging.debug('Posted text: ' + text_content)

                        # Post to Mattermost
                        post_text(text_content, feed.User, feed.Channel,
                                  feed.Iconurl)
                else:
                    if not silent_mode:
                        logging.debug('{} no new feed items'.format(feed.Name))
            except Exception as e:
                logging.error('Could not fetch %s', feed.Url)
                logging.exception(e)
                continue

        time.sleep(delay_between_pulls)
