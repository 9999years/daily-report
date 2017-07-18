import twitter
import datetime
import dates
import textwrap

# local
import prefs

def get_api():
    return twitter.Api(
        consumer_key=prefs.keys['twitter']['consumer_key'],
        consumer_secret=prefs.keys['twitter']['consumer_secret'],
        access_token_key=prefs.keys['twitter']['access_token'],
        access_token_secret=prefs.keys['twitter']['access_token_secret']
    )

def get_tweets(user='dril'):
    api = get_api()
    return api.GetUserTimeline(screen_name=user)

def get_date(tweet):
    # Tue Jul 18 03:44:48 +0000 2017
    return datetime.datetime.strptime(tweet.created_at,
        '%a %b %d %H:%M:%S %z %Y')

def format(tweet):
    date = get_date(tweet)
    return (textwrap.fill(f'@{tweet.user.screen_name}: {tweet.text}',
            width=prefs.prefs['width'])
        + f'{tweet.favorite_count} likes, {tweet.retweet_count} rts\n'
        + datetime.datetime.strftime(date, '%Y-%m-%d %I:%M:%S %p'))

def last(user='dril'):
    tweets = get_tweets(user)
    valid = []
    today, tomorrow = dates.today_times()
    yesterday = today - datetime.timedelta(days=1)
    for tweet in tweets:
        if tweet.in_reply_to_screen_name is not None:
            # skip @s
            continue
        date = get_date(tweet)
        if date > yesterday:
            valid.append(format(tweet))
    return valid
