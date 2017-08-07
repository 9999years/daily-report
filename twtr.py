import twitter
import datetime
import dates
import textwrap

# local
from prefs import prefs, keys
from formatter import extformat
import misc

def get_api():
    return twitter.Api(
        consumer_key=keys['twitter']['consumer_key'],
        consumer_secret=keys['twitter']['consumer_secret'],
        access_token_key=keys['twitter']['access_token'],
        access_token_secret=keys['twitter']['access_token_secret']
    )

def get_tweets(user='dril'):
    api = get_api()
    return api.GetUserTimeline(screen_name=user)

def get_date(tweet):
    """Tue Jul 18 03:44:48 +0000 2017
    """
    return datetime.datetime.strptime(tweet.created_at,
        '%a %b %d %H:%M:%S %z %Y')

def format_tweet(tweet, style=None):
    fvars = tweet.AsDict()
    fvars.update({
        'date': get_date(tweet),
    })
    fvars.update({
        'pretty_text': misc.fill(extformat(
            prefs['twitter']['pretty_format'],
            fvars, text=tweet.text.replace('\n', '\n\n')))
    })
    if style == '__bot__':
        # "pythonic"
        fstr = prefs['twitter']['bot_format']
    elif style is not None:
        fstr = style
    else:
        fstr = prefs['twitter']['format']
    return extformat(fstr, fvars)

def since_yesterday(user='dril'):
    tweets = get_tweets(user)
    valid = []
    today, tomorrow = dates.today_times()
    yesterday = today - datetime.timedelta(days=1)
    now = datetime.datetime.now()
    for tweet in tweets:
        if tweet.in_reply_to_screen_name is not None:
            # skip @s
            continue
        date = get_date(tweet)
        if date > yesterday:
            valid.append(tweet)
    return valid

def last(user='dril', style=None):
    tweets = since_yesterday(user)
    return format_tweet(tweets[0], style=style) if len(tweets) > 0 else ''

def bot(user='tiny_star_field'):
    return last(user, style='__bot__')
