import datetime
import prefs
from collections import namedtuple
# google calendar
import httplib2
from apiclient import discovery
# gcal date parsing
import re

# local
import misc
import gen_credentials as creds

def timezone():
    delt = datetime.datetime.now() - datetime.datetime.utcnow()
    # round to the nearest second for some unix nonsense
    # if delt.microseconds is not 0:
        # delt = delt + datetime.timedelta(
            # seconds=1 if delt.microseconds > 500000 else -1)
        # delt = delt.replace(microseconds=0)
    delt -= datetime.timedelta(microseconds=delt.microseconds)
    # round to nearest minute
    extra_secs = delt.seconds % 60
    if extra_secs is not 0:
        delt += datetime.timedelta(
            seconds=60 - extra_secs if extra_secs >= 30 else -extra_secs
        )
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
    credentials = creds.credentials(prefs.prefs)
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

def events():
    Event = namedtuple('Event', ['start', 'end', 'duration', 'info'])
    out = ''
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

    def print_event(time, event):
        margin = 9
        leader_visual = '|'
        leader = ' ' * (margin - len(leader_visual))
        width = prefs.prefs['width'] - margin - 1
        summary = textwrap.wrap(
            event.info['summary'], width=width)
        out += f'{time} {leader_visual} {summary.pop(0)}'
        for line in summary:
            out += (f'{leader}{leader_visual} {line}')

    for event in alldays:
        print_event('all day', event)

    out += misc.hrule()

    for event in todays:
        print_event(hours(event.start), event)

    return out

def today_date():
    return 'today is ' + today_times()[0].strftime('%A, %B %d').lower()

def iso_date():
    return misc.left_pad(
        today_times()[0].strftime('%Y-%m-%d'), prefs.prefs['width'])
