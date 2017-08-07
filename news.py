from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

from prefs import prefs
import misc
from formatter import extformat

cache = {}

def url(postfix):
    return 'http://feeds.reuters.com/reuters/' + postfix

def feed_parser(postfix='topNews'):
    if postfix not in cache:
        feed = requests.get(url(postfix))
        cache[postfix] = BeautifulSoup(feed.text, 'html.parser')
    return cache[postfix]

def stories(postfix='topNews'):
    parser = feed_parser(postfix)
    ret = []
    for s in parser.find_all('item'):
        ret.append(s)
    return ret

def format_story(story):
    desc = BeautifulSoup(story.description.text, 'html.parser')
    pubdate = datetime.strptime(
            story.pubdate.text,
            '%a, %d %b %Y %H:%M:%S %z')
    return extformat(prefs['news']['format'],
        description=desc.text,
        title=story.title.text,
        url=story.guid.text,
        short_url=misc.shorten_pretty(story.guid.text),
        date=pubdate,
        )

def headlines(zone='topNews', amount=3):
    ret = []
    for i, story in zip(range(amount), stories(zone)):
        ret.append(format_story(story))
    return '\n'.join(ret)
