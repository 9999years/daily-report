import twitter
import datetime
import dates
import textwrap

# local
from prefdicts import prefs, keys
from extendedformatter import extformat
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

def format_tweet(tweet):
    date = get_date(tweet)
    pretty_text = misc.fill(tweet.text.replace('\n', '\n\n'))
    return extformat(prefs['twitter']['tweet_format'], tweet.AsDict(), date=date)

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
            valid.append(format_tweet(tweet))
    return valid

def last(user='dril'):
    tweets = since_yesterday(user)
    return tweets[0] if len(tweets) > 0 else ''
