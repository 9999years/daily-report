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

def npr(section):
    sections = {
        'News'         : '1001',
        'News'         : '1002',
        'World'        : '1004',
        'Business'     : '1006',
        'Science'      : '1007',
        'Iraq'         : '1010',
        'Politics'     : '1012',
        'Education'    : '1013',
        'Politics'     : '1014',
        'Race'         : '1015',
        'Religion'     : '1016',
        'Economy'      : '1017',
        'Technology'   : '1019',
        'Media'        : '1020',
        'Interviews'   : '1022',
        'Environment'  : '1025',
        'Space'        : '1026',
        'Books'        : '1032',
        'Music'        : '1039',
        'Movies'       : '1045',
        'Diversions'   : '1051',
        'Food'         : '1053',
        'Gardening'    : '1054',
        'Sports'       : '1055',
        'Opinion'      : '1057',
        'Columns'      : '1058',
        'Analysis'     : '1059',
        'Remembrances' : '1062',
        'Holidays'     : '1065',
        'Law'          : '1070',
        'Summer'       : '1088',
        'Concerts'     : '1109',
        'Governing'    : '1123',
        'Europe'       : '1124',
        'Asia'         : '1125',
        'Africa'       : '1126',
        'Health'       : '1128',
        'Humans'       : '1129',
        'Energy'       : '1131',
        'Animals'      : '1132',
        'History'      : '1136',
        'Television'   : '1138',
        'Recipes'      : '1139',
        'Architecture' : '1142',
        'Photography'  : '1143',
        'Theater'      : '1144',
        'Dance'        : '1145',
        'Multimedia'   : '1147',
        'Afghanistan'  : '1149',
    }

    return 'http://www.npr.org/rss/rss.php?id=' + sections[section]

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

    timefmtprefix = '%a, %d %b %Y %H:%M:%S'
    try:
        pubdate = datetime.strptime(story.pubdate.text, timefmtprefix + ' %z')
    except ValueError:
        try:
            # possibly a named timezone
            pubdate = datetime.strptime(story.pubdate.text, timefmtprefix + ' %Z')
        except ValueError:
            try:
                # fuck the timezone
                pubdate = datetime.strptime(
                    story.pubdate.text[:story.pubdate.text.rfind(' ')],
                    timefmtprefix)
            except ValueError:
                # FUCK THE TIME
                pubdate = datetime.min

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
