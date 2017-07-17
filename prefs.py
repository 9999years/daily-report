import json

def json_from_file(fname):
    with open(fname) as f:
        return json.loads(f.read())
    return None

def prefs(pref_path='prefs.json'):
    prefs = json_from_file(pref_path)
    keys  = json_from_file(prefs['api_keys'])
    return prefs, keys
