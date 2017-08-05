import datetime
from collections import namedtuple
# google calendar
import httplib2
from apiclient import discovery
# gcal date parsing
import re
import textwrap

# local
import misc
import gen_credentials as creds
from prefs import prefs, keys

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

def today_events(calendar='primary', day=0, **kwargs):
    credentials, http, service = creds.build_creds()
    today, tomorrow = today_times()

    tomorrow += datetime.timedelta(days=day)
    today    += datetime.timedelta(days=day)

    args = {
        'calendarId':    calendar,
        'orderBy':       'startTime',
        'singleEvents':  True,
        'timeMin':       today.isoformat(),
        'timeMax':       tomorrow.isoformat()
    }

    args.update(kwargs)

    eventsResult = service.events().list(**args).execute()
    return eventsResult.get('items', [])

def list_calendars():
    credentials, http, service = creds.build_creds()
    return service.calendarList().list().execute()['items']

def calendar_match(pat, regex=True):
    cals = list_calendars()
    outs = []
    for cal in cals:
        if regex and re.search(pat, cal['summary'], flags=re.IGNORECASE):
            outs.append(cal)
        elif pat in cal['summary']:
            outs.append(cal)
    return outs

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

    event['start']    = time_parse('start')
    event['end']      = time_parse('end')
    event['duration'] = event['end'] - event['start']
    return event

def format_event(time, event):
    leader = ' ' + prefs['vert'] + ' '
    if time == 'all day' and event['duration'].days > 1:
        event['summary'] += (' (day '
            + str((today - event['start']).days) + ' of '
            + str((event['end'] - event['start']).days) + ')')

    return misc.format_left(event['summary'],
        leader=leader, firstline=time + leader)

def format_todos(todos):
    """takes a list of strings and returns a formatted list of todos"""
    ret = ''
    for todo in todos:
        ret += misc.format_left(todo,
            firstline=prefs['calendar']['todo_check'])
    return ret

def today_todos():
    todos = []
    todo_cals = calendar_match(prefs['calendar']['todo_pat'])
    for cal in todo_cals:
        todos.extend(today_events(cal['id'], orderBy='updated'))

    todo_list = []
    for todo in todos:
        todo_list.append(todo['summary'])

    ret = format_todos(todo_list)

    return ret.rstrip()

def today_countdowns():
    today, tomorrow = today_times()
    countdown_cals = calendar_match(prefs['calendar']['countdown_pat'])

    def days_until(event):
        return str((event['start'] - today).days)

    ret = ''
    def add_countdown(event):
        nonlocal ret
        event['summary'] += event['start'].strftime(' (%Y-%m-%d)')
        leader = ' ' + prefs['vert'] + ' '
        ret += misc.format_left(event['summary'],
            leader=leader,
            firstline=days_until(event).rjust(left_width) + leader)

    countdowns = []
    for cal in countdown_cals:
        events = (today_events(calendar=cal['id'],
            maxResults=prefs['calendar']['max_countdowns'],
            timeMax=None))
        for event in events:
            countdowns.append(event_times(event))

    if len(countdowns) is 0:
        return ''

    countdowns = sorted(countdowns, key=lambda k: k['start'])

    left_width = len(days_until(countdowns[-1]))

    for countdown in countdowns:
        add_countdown(countdown)

    return ret.rstrip()

def today_work():
    work_cals = calendar_match(prefs['calendar']['work_pat'])

    shifts = []
    for cal in work_cals:
        shifts.extend(today_events(cal['id']))

    out = ''
    for shift in shifts:
        shift = event_times(shift)
        out += format_event(misc.hoursminutes(shift['start']), shift)

    return out.rstrip()

def events(day=0):
    today, tomorrow = today_times()

    events = today_events(day=day)
    alldays = []
    todays = []
    for event in events:
        event = event_times(event)
        if event['start'] <= today and event['end'] >= tomorrow:
            alldays.append(event)
        else:
            todays.append(event)

    out = ''
    for event in alldays:
        out += format_event(prefs['dates']['all_day'], event)

    out += misc.thinhrule() + '\n'

    for event in todays:
        out += format_event(misc.hoursminutes(event['start']), event)

    return out.rstrip()

def today_date(day=0):
    return (today_times()[0] + datetime.timedelta(days=day)).strftime(
        prefs['dates']['today_format'])

def now_hm(fillchar=''):
    return misc.hoursminutes(datetime.datetime.now(), pad=fillchar)

def iso_date():
    return today_times()[0].strftime('%Y-%m-%d')
