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

def credentials(prefs):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    cred_path = os.path.abspath(prefs['credential_path'])
    store = Storage(prefs['credential_path'])
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(
            prefs['google_key_path'], prefs['calendar_scope']
        )
        flow.user_agent = prefs['app_name']
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials')
    return credentials

if __name__ is '__main__':
    print(credentials())
