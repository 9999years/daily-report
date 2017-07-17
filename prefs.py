import json

def json_from_file(fname):
    with open(fname) as f:
        return json.loads(f.read())
    return None

global prefs
global keys

def get_prefs(pref_path='prefs.json'):
    global prefs
    global keys
    prefs = json_from_file(pref_path)
    keys  = json_from_file(prefs['api_keys'])
    return prefs, keys

load_prefs = get_prefs
