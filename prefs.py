import json
from os import path

global prefs_dir
global prefs
global keys

class JsonContainer(dict):
    def __init__(self, src, encoding='utf-8'):
        self.encoding = encoding

        if isinstance(src, str):
            self.path = src
            self.refresh()
        elif isinstance(src, dict):
            self.dict = src
            self.path = None

        self.refreshmethods()

    def refresh(self):
        with open(self.path, encoding=self.encoding) as f:
            self.dict = json.loads(f.read())
        if self.path is not None:
            self.directory = path.abspath(path.dirname(self.path))

    def __getitem__(self, key):
        return self.dict.__getitem__(key)

    def refreshmethods(self):
        # inheritance???
        methods = ['clear', 'copy', 'fromkeys', 'get', 'items', 'keys', 'pop',
            'popitem', 'setdefault', 'update', 'values', '__str__', '__repr__',
            '__setitem__', '__getitem__']

        for method in methods:
            setattr(self, method, getattr(self.dict, method))

    def fname(self, *route):
        """
        takes the route of a key in this that represents a filename relative
        to the json source and returns the absolute filename.

        route is passed as tuples
        eg. if the key would be accessed as this['x']['y'], call
        fname('x', 'y')
        """
        final = self.dict
        for key in route:
            final = final[key]
        if not isinstance(final, str):
            raise ValueError('Route did not lead to a string key in prefs')
        else:
            return path.join(self.directory, final)

def get_prefs(pref_path=None, encoding='utf-8'):
    global prefs
    global keys
    global prefs_dir
    # get script directory
    here = path.abspath(path.dirname(__file__))
    if pref_path is None:
        # pref_path_path contains a relative path to the prefs.json file
        # a Reasonable Default (tm)
        rel_pref_path_path = 'pref_path.txt'
        # absolute version
        abs_pref_path_path = path.join(here, rel_pref_path_path)
        if path.isfile(abs_pref_path_path):
            # if the pref path path exists, use it
            with open(abs_pref_path_path) as f:
                pref_path = f.read()
        else:
            # otherwise, assume prefs.json
            pref_path = path.join(here, 'prefs.json')

    # what directory is prefs.json in? we'll need it later to get filenames
    # from keys
    prefs_dir = path.abspath(path.dirname(pref_path))
    prefs = JsonContainer(pref_path, encoding=encoding)
    keys  = JsonContainer(prefs.fname('api_keys'), encoding=encoding)
    return prefs, keys

prefs, keys = get_prefs()
