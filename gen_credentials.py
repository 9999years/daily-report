import httplib2
from apiclient import discovery
import oauth2client as oauth

import os

# local
import prefs

def credentials(prefs):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    cred_path = os.path.abspath(prefs['credential_path'])
    store = oauth.file.Storage(prefs['credential_path'])
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = oauth.client.flow_from_clientsecrets(
            prefs['google_key_path'], prefs['calendar']['scope']
        )
        flow.user_agent = prefs['app_name']
        credentials = oauth.tools.run_flow(flow, store, flags)
        print('Storing credentials')
    return credentials

def build_creds(api='calendar', version='v3'):
    creds = credentials(prefs.prefs)
    http = creds.authorize(httplib2.Http())
    service = discovery.build(api, 'v3', http=http)
    return creds, http, service

if __name__ is '__main__':
    print(credentials())
