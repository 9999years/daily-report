from bs4 import BeautifulSoup
import requests
import re
from datetime import datetime

from prefs import prefs
import misc
from formatter import extformat

cache = {}

def reuters(postfix):
    return 'http://feeds.reuters.com/reuters/' + postfix

def nytimes(postfix):
    return f'http://rss.nytimes.com/services/xml/rss/nyt/{postfix}.xml'

def cnn(postfix):
    return f'http://rss.cnn.com/rss/cnn_{postfix}.rss'

def feed_parser(url=reuters('worldnews')):
    if url not in cache:
        feed = requests.get(url)
        cache[url] = BeautifulSoup(feed.text, 'html.parser')
    return cache[url]

def stories(url=reuters('worldnews')):
    parser = feed_parser(url)
    ret = []
    for s in parser.find_all('item'):
        ret.append(s)
    return ret

def format_story(story):
    desc = BeautifulSoup(story.description.text, 'html.parser')
    head = BeautifulSoup(story.title.text, 'html.parser')
    timefmt = '%a, %d %b %Y %H:%M:%S %z'
    try:
        pubdate = datetime.strptime(story.pubdate.text, timefmt)
    except ValueError:
        timefmt = '%a, %d %b %Y %H:%M:%S %Z'
        pubdate = datetime.strptime(story.pubdate.text, timefmt)
    return extformat(prefs['news']['format'],
        description=desc.text,
        title=head.text,
        url=story.guid.text,
        short_url=misc.shorten_pretty(story.guid.text),
        date=pubdate,
        )

def headlines(url=reuters('worldnews'), amount=3):
    """
    list of zones: https://www.reuters.com/tools/rss
    """
    ret = []
    for i, story in zip(range(amount), stories(url)):
        ret.append(format_story(story))
    return '\n'.join(ret)

def headline(url=reuters('worldnews')):
    """
    alias for headlines(url, amount=1)
    """
    return headlines(url, amount=1)

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Generates headline summaries from prefs.json and RSS urls'
    )

    parser.add_argument('url', type=str, nargs='+',
        default='http://rss.nytimes.com/services/xml/rss/nyt/World.xml',
        help='rss url to parse')

    parser.add_argument('-n', '--number', type=int,
        default='10', help='amount of stories to show, per-url')

    args = parser.parse_args()

    for url in args.url:
        print(headlines(url, amount=args.number))

if __name__ == '__main__':
    main()
