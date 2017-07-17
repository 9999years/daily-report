import json
from os import path

def json_from_file(fname):
    with open(fname) as f:
        return json.loads(f.read())
    return None

global prefs
global keys

def get_prefs(pref_path=None):
    global prefs
    global keys
    pref_path_path = 'pref_path.txt'
    if pref_path is None:
        if path.isfile(pref_path_path):
            with open(pref_path_path) as f:
                pref_path = f.read()
        else:
            pref_path='prefs.json'
    prefs = json_from_file(pref_path)
    keys  = json_from_file(prefs['api_keys'])
    return prefs, keys

load_prefs = get_prefs

get_prefs()
