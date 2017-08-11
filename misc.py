import textwrap
import datetime
import re
import subprocess
import shlex
import requests
import json
from time import sleep

import gen_credentials as creds

# local
from prefs import prefs, keys

def fill(*txt, width=prefs['width'], joiner='\n\n', **kwargs):
    def fill_fn(msg):
        return textwrap.fill(msg, width=width, **kwargs)
    return joiner.join(map(fill_fn, ''.join(txt).split(joiner)))

def left(txt, width=prefs['width'], fillchar=' '):
    return txt.ljust(width, fillchar)

# keep procedural public api
def right(txt, width=prefs['width'], fillchar=' '):
    return txt.rjust(width, fillchar)

left_pad = right

def hrule():
    return prefs['horiz'] * prefs['width']

def thinhrule():
    return prefs['horiz_light'] * prefs['width']

def lerp(min, max, amt):
    """Interpolate from min to max by amt"""
    return amt * (max - min) + min

def between(min, max, val):
    """fraction val is between min and max"""
    return (val - min) / (max - min)

def scale(val, min, max, omin, omax):
    """linear map from a∈[min, max] → b∈[omin, omax]"""
    return (val - min) / (max - min) * (omax - omin) + omin

def format_left(txt, leader='',
        firstline=None, align_leader='right', margin='firstline', splitter='\n'):
    firstline = firstline or leader
    margin = len(firstline)
    leader = leader.rjust(margin) if align_leader == 'right' else leader
    width = prefs['width'] - margin
    lines = textwrap.wrap(txt, width=width)
    out = f'{firstline}{lines.pop(0)}\n'
    for line in lines:
        out += (f'{leader}{line}\n')
    return out.rstrip()

def center(txt, width=prefs['width'], fillchar=' '):
    return txt.center(width, fillchar)

def align(left='', center='', right='', width=prefs['width'], fillchar=' '):
    """
    returns a string aligned to `width`, with `left`, `right`, and `center` at
    their respective locations in the string. `center` will destructively
    overwrite `left` and `right`, and `left` will overwrite `right`.

    like a stronger left_pad
    """
    lr = left + right.rjust(width, fillchar)[len(left):]

    c = width // 2
    halfc = int(c - len(center) / 2)

    return lr[:halfc] + center + lr[halfc + len(center):]

def hoursminutes(time, fillchar=' '):
    fmt = '%I'
    if prefs['dates']['hours'] == 24:
        # 24 hr time
        fmt = '%H'
    fmt += ':%M'
    if prefs['dates']['hours'] == 12:
        # add am/pm
        fmt += '%p'

    # pad with spaces instead of 0s
    # only replaces the first digit so we don’t have to worry about
    # 00 oclock in 24hr time
    ret = format(time, fmt)
    if ret[0] == '0':
        ret = fillchar + ret[1:]
    return ret

def formatdelta(time):
    days = time.days
    hrs  = time.seconds // 3600 # 60 × 60
    secs = time.seconds  % 3600
    mins = secs // 60
    secs = secs  % 60
    ret = ''
    if days != 0:
        ret += f'{days} days, '
    ret += f'{hrs: 2}:{mins:02}'
    if secs != 0:
        ret += f'::{secs:02}'
    return ret

def deduplicate_rules(msg):
    # empty sections surrounded by hrules can look silly
    # make them one hrule instead
    # replace multiple thin hrules with one thinhrule
    msg = re.sub('((' + thinhrule() + r')\n*){2,}',
        thinhrule() + '\n', msg)
    # but all regular hrules or mixed thin/regular hrules turn into regular
    # hrules
    return re.sub('((' + hrule() + '|' + thinhrule() + r')\n*){2,}',
        hrule() + '\n', msg)

def shell(prog, opts=[]):
    dispatch = shlex.split(prog)
    dispatch.extend(opts)
    result = subprocess.run(dispatch, stdout=subprocess.PIPE)
    return result.stdout.decode('utf-8')

def shorten(url, **kwargs):
    credentials, http, service = creds.build_creds('urlshortener', 'v1')
    result = service.url().insert(body={
        'longUrl': url }, **kwargs).execute()
    return result['id']

def shorten_pretty(url, **kwargs):
    longer = shorten(url, **kwargs)
    return longer[longer.index(':') + 3:]

def request_backbone(url, cache, process=None):
    # already made this request? don't make it again!
    # TODO maybe add a time limit for cache validity
    if url not in cache:
        # request and retry up to `retries` times
        for i in range(prefs['max_retries']):
            r = requests.get(url)
            if r.status_code == requests.codes.ok:
                break
            else:
                # wait a second if we failed --- don't hammer the api
                sleep(1)

        cache[url] = process(r) if process is not None else r
    return cache[url], cache

def request_json(url, cache, process=None):
    ret, cache = request_backbone(url, cache, process)
    if isinstance(cache[url], requests.Response):
        cache[url] = ret.json()
    return cache[url], cache

def request(url, cache, process=None):
    ret, cache = request_backbone(url, cache, process)
    if isinstance(cache[url], requests.Response):
        cache[url] = ret.text
    return cache[url], cache

def json_from_file(fname, encoding='utf-8'):
    with open(fname, encoding=encoding) as f:
        return json.loads(f.read())
    return None

def listifier(obj):
    if (not isinstance(obj, list)
        and not isinstance(obj, tuple)):
        obj = [obj]
    return obj
