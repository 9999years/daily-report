import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
import json
import requests
from urllib import parse as urlparse

import argparse
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

def json_from_file(fname):
    with open(fname) as f:
        return json.loads(f.read())
    return None

pref_path = 'prefs.json'
prefs = json_from_file(pref_path)

keys = json_from_file(prefs['api_keys'])

def get_weather():
    url = ('http://api.wunderground.com/api/' + keys['wunderground']
        + '/hourly/q/{state}/{city}.json'.format_map(prefs['location']))
    r = requests.get(url)
    return r.json()


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = Storage(prefs['credential_path'])
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(prefs['google_key_path'], prefs['calendar_scope'])
        flow.user_agent = prefs['app_name']
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials')
    return credentials

def get_today_events():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    # get today at midnight and tomorrow at midnight so we can fetch events for
    # today
    zone = datetime.timezone(
        datetime.datetime.now() - datetime.datetime.utcnow()
    )
    today = datetime.datetime.now(tz=zone).replace(
        hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + datetime.timedelta(days=1)

    print('start = ', today.isoformat())
    print('end =   ', tomorrow.isoformat())

    eventsResult = service.events().list(
        calendarId='primary', singleEvents=True, orderBy='startTime',
        timeMin=today.isoformat(), timeMax=tomorrow.isoformat()).execute()
    events = eventsResult.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])

def main():
    import pprint
    pp = pprint.PrettyPrinter(indent=1, compact=True)
    pp.pprint(get_weather())

if __name__ == '__main__':
    main()
