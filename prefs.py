import json
from os import path

def json_from_file(fname, encoding='utf-8'):
    with open(fname, encoding=encoding) as f:
        return json.loads(f.read())
    return None

global prefs
global keys

def get_prefs(pref_path=None, encoding='utf-8'):
    global prefs
    global keys
    pref_path_path = 'pref_path.txt'
    if pref_path is None:
        if path.isfile(pref_path_path):
            with open(pref_path_path) as f:
                pref_path = f.read()
        else:
            pref_path='prefs.json'
    prefs = json_from_file(pref_path, encoding=encoding)
    keys  = json_from_file(prefs['api_keys'], encoding=encoding)
    return prefs, keys

load_prefs = get_prefs

get_prefs()
