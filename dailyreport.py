#! /usr/local/bin/python3

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import json
import requests
from urllib import parse as urlparse
import os
import re

from collections import namedtuple

import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

# local imports
import gen_credentials as creds
import prefs

global prefs
global keys

def timezone():
    delt = datetime.datetime.now() - datetime.datetime.utcnow()
    # round to the nearest second for some unix nonsense
    # if delt.microseconds is not 0:
        # delt = delt + datetime.timedelta(
            # seconds=1 if delt.microseconds > 500000 else -1)
        # delt = delt.replace(microseconds=0)
    delt = delt.replace(microseconds=0)
    # round to nearest minute
    if delt.seconds % 60 is not 0:
        delt = delt.replace(seconds=round(delt.seconds / 60) * 60)
    print(delt)
    return datetime.timezone(delt)


def today_times():
    # get today at midnight and tomorrow at midnight so we can fetch
    # events for today
    zone = timezone()

    today = datetime.datetime.now(tz=zone).replace(
        hour=0, minute=0, second=0, microsecond=0)

    tomorrow = today + datetime.timedelta(days=1)

    return today, tomorrow


def today_events():
    credentials = creds.credentials(prefs)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    today, tomorrow = today_times()

    eventsResult = service.events().list(
        calendarId='primary', singleEvents=True, orderBy='startTime',
        timeMin=today.isoformat(), timeMax=tomorrow.isoformat()).execute()
    events = eventsResult.get('items', [])

    return events

def event_times(event):
    '''takes a google calendar event, returns the start / end times and
    duration as a 3-tuple
    '''
    dt_format = '%Y-%m-%dT%H:%M:%S%z'
    d_format  = '%Y-%m-%d'
    # yyyy-mm-ddThh-mm-ss±hh:mm
    # cutting out timezones (±hh:mm)
    # could also validate with
    # [+-](2[0-4]|[01]\d):[0-5]\d
    # or really
    # [+-](2[0-3]|[01]\d):(00|30)
    # if we're being strict about it
    # but uhhh if you wanna live in utc-99:00 thats none of my business
    tz_regex = re.compile(r'([+-]\d{2}):(\d{2})')
    tz_replace = r'\1\2'
    format_timezone = lambda tz_str: re.sub(tz_regex, tz_replace, tz_str)

    # work for yyyy-mm-dd AND yyyy-mm-ddThh-mm-ss±hh:mm formats
    # fortunately, iso date = 'date' key, iso datetime = 'datetime' key.
    # thanks google!
    date = lambda key: (
        (format_timezone(event[key]['dateTime']), dt_format)
        if 'dateTime' in event[key] else (event[key]['date'], d_format))

    zone = timezone()

    time_parse = lambda key: (
        datetime.datetime.strptime(*date(key)).replace(tzinfo=zone))

    start = time_parse('start')
    end   = time_parse('end')
    duration = end - start
    return (start, end, duration)

def hours(time):
    hours = datetime.datetime.strftime(time, '%I')
    # pad with spaces instead of 0s
    i = 0
    while hours[i] is '0' and i < len(hours):
        hours = hours[:i] + ' ' + hours[i + 1:]
    return hours + ':' + datetime.datetime.strftime(time, '%M%p')

def main():
    # import pprint
    # pp = pprint.PrettyPrinter(indent=1, depth=2)
    # graph_weather()
    Event = namedtuple('Event', ['start', 'end', 'duration', 'info'])
    today, tomorrow = today_times()
    events = today_events()
    alldays = []
    todays = []
    for event in events:
        start, end, duration = event_times(event)
        if start <= today and end >= tomorrow:
            alldays.append(Event(
                start=start, end=end, duration=duration, info=event))
        else:
            todays.append(Event(
                start=start, end=end, duration=duration, info=event))

    for event in alldays:
        print('ALL DAY: ', event.info['summary'])

    for event in todays:
        print(hours(event.start), ' - ', event.info['summary'])

if __name__ == '__main__':
    prefs, keys = prefs.prefs()
    main()
